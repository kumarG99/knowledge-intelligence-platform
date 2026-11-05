"""Run a small evaluation suite against the KIP RAG pipeline."""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from app.db.session import SessionLocal
from app.services.rag import answer_question

EVALUATION_DIR = Path(__file__).resolve().parent
DATASET_PATH = EVALUATION_DIR / "questions.json"
REPORT_DIR = EVALUATION_DIR / "reports"

REFUSAL_ANSWER = "I don't know based on the provided documents."


def evaluate_answer(
    case: dict,
    answer: str,
    source_count: int,
) -> bool:
    """Check expected content and basic citation validity."""

    citations = [int(number) for number in re.findall(r"\[(\d+)\]", answer)]

    if case["category"] == "unanswerable":
        return answer.strip().casefold() == REFUSAL_ANSWER.casefold() and not citations

    expected_keywords = case.get("expected_keywords", [])

    keywords_present = all(
        keyword.casefold() in answer.casefold() for keyword in expected_keywords
    )

    citations_present = bool(citations)

    citations_valid = all(1 <= citation <= source_count for citation in citations)

    return keywords_present and citations_present and citations_valid


def run_evaluation(organization_id: UUID) -> None:
    """Evaluate all dataset questions against one organization."""

    cases = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    results = []

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    with SessionLocal() as db:
        for case in cases:
            print(f"\nRunning {case['id']}: {case['question']}")

            try:
                response = answer_question(
                    db=db,
                    organization_id=organization_id,
                    question=case["question"],
                    limit=3,
                )

                passed = evaluate_answer(
                    case,
                    response.answer,
                    len(response.sources),
                )

                source_pages = [source.page_number for source in response.sources]

                expected_page = case.get("expected_page")

                citation_page_found = (
                    expected_page in source_pages if expected_page is not None else None
                )

                result = {
                    "id": case["id"],
                    "category": case["category"],
                    "question": case["question"],
                    "answer": response.answer,
                    "passed": passed,
                    "expected_page": expected_page,
                    "expected_page_retrieved": citation_page_found,
                    "sources": [
                        {
                            "filename": source.filename,
                            "page_number": source.page_number,
                            "similarity": source.similarity,
                        }
                        for source in response.sources
                    ],
                    "model": response.model,
                    "input_tokens": response.input_tokens,
                    "output_tokens": response.output_tokens,
                    "duration_seconds": response.duration_seconds,
                }

                print(f"Answer: {response.answer}")
                print(f"Result: {'PASS' if passed else 'FAIL'}")

            except Exception as exc:
                db.rollback()
                result = {
                    "id": case["id"],
                    "category": case["category"],
                    "question": case["question"],
                    "passed": False,
                    "error": f"{type(exc).__name__}: {exc}",
                }

                print(f"ERROR: {result['error']}")

            results.append(result)

    passed_count = sum(result["passed"] for result in results)

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "organization_id": str(organization_id),
        "total": len(results),
        "passed": passed_count,
        "failed": len(results) - passed_count,
        "pass_rate": (round(passed_count / len(results) * 100, 2) if results else 0.0),
        "results": results,
    }

    report_path = REPORT_DIR / "latest.json"
    report_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print("\n========== EVALUATION SUMMARY ==========")
    print(f"Total: {report['total']}")
    print(f"Passed: {report['passed']}")
    print(f"Failed: {report['failed']}")
    print(f"Pass rate: {report['pass_rate']}%")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m evaluations.run_evaluation <organization_id>")
        sys.exit(1)

    run_evaluation(UUID(sys.argv[1]))
