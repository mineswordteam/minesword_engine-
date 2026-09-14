"""Persian Search Quality Benchmark Evaluation Suite for Minesword Engine."""

import math
from typing import Dict, List, Any
from minesword.db import Database
from minesword.search_engine import SearchEngine
from minesword.seed_data import seed_database_if_empty

BENCHMARK_QUERIES = [
    {
        "query": "دانلود کالاف دیوتی موبایل",
        "expected_domains": ["farsroid.com", "yasdl.com", "soft98.ir"]
    },
    {
        "query": "دانلود کالاف دیوتی وارزون",
        "expected_domains": ["yasdl.com", "soft98.ir", "zoomg.ir"]
    },
    {
        "query": "بهترین لپ تاپ برای برنامه نویسی",
        "expected_domains": ["zoomit.ir", "digikala.com", "torob.com"]
    },
    {
        "query": "قیمت لپ تاپ",
        "expected_domains": ["digikala.com", "torob.com", "zoomit.ir"]
    },
    {
        "query": "آموزش پایتون",
        "expected_domains": ["maktabkhooneh.org", "faradars.org", "python.org"]
    },
    {
        "query": "اخبار فوتبال ایران",
        "expected_domains": ["varzesh3.com", "football360.ir", "tasnimnews.com"]
    },
    {
        "query": "اخبار پرسپولیس",
        "expected_domains": ["varzesh3.com", "football360.ir", "perspolisnews.com"]
    },
    {
        "query": "Stronghold Crusader دانلود",
        "expected_domains": ["yasdl.com", "soft98.ir", "fa.wikipedia.org"]
    },
    {
        "query": "ویندوز ۱۱",
        "expected_domains": ["soft98.ir", "p30download.ir", "zoomit.ir"]
    },
    {
        "query": "حل مشکل وای فای ویندوز",
        "expected_domains": ["soft98.ir", "zoomit.ir", "sarzamindownload.com"]
    },
    {
        "query": "بهترین کارت گرافیک",
        "expected_domains": ["lioncomputer.com", "zoomit.ir", "zoomg.ir"]
    }
]


def calculate_precision_at_k(results: List[Dict[str, Any]], expected_domains: List[str], k: int = 5) -> float:
    top_k = results[:k]
    if not top_k:
        return 0.0
    relevant_count = sum(1 for r in top_k if any(dom in r.get("domain", "").lower() for dom in expected_domains))
    return float(relevant_count) / float(k)


def calculate_mrr(results: List[Dict[str, Any]], expected_domains: List[str]) -> float:
    for rank, r in enumerate(results, start=1):
        if any(dom in r.get("domain", "").lower() for dom in expected_domains):
            return 1.0 / rank
    return 0.0


def calculate_ndcg(results: List[Dict[str, Any]], expected_domains: List[str], k: int = 5) -> float:
    top_k = results[:k]
    dcg = 0.0
    for idx, r in enumerate(top_k, start=1):
        rel = 1.0 if any(dom in r.get("domain", "").lower() for dom in expected_domains) else 0.0
        dcg += (2**rel - 1) / math.log2(idx + 1)

    idcg = sum((2**1.0 - 1) / math.log2(idx + 1) for idx in range(1, min(len(expected_domains), k) + 1))
    return float(dcg / idcg) if idcg > 0 else 0.0


def run_benchmark(db_path: str = "minesword.db") -> Dict[str, Any]:
    db = Database(db_path)
    seed_database_if_empty(db)
    se = SearchEngine(db)

    metrics_list = []
    for item in BENCHMARK_QUERIES:
        q = item["query"]
        expected = item["expected_domains"]

        res = se.search(q, page=1, page_size=10)
        results = res.get("results", [])

        p5 = calculate_precision_at_k(results, expected, k=5)
        mrr = calculate_mrr(results, expected)
        ndcg5 = calculate_ndcg(results, expected, k=5)
        recall = 1.0 if results else 0.0

        metrics_list.append({
            "query": q,
            "total_found": res.get("total", 0),
            "P@5": round(p5, 3),
            "MRR": round(mrr, 3),
            "NDCG@5": round(ndcg5, 3),
            "Recall": round(recall, 3)
        })

    avg_p5 = sum(m["P@5"] for m in metrics_list) / len(metrics_list)
    avg_mrr = sum(m["MRR"] for m in metrics_list) / len(metrics_list)
    avg_ndcg5 = sum(m["NDCG@5"] for m in metrics_list) / len(metrics_list)
    avg_recall = sum(m["Recall"] for m in metrics_list) / len(metrics_list)

    return {
        "queries_count": len(BENCHMARK_QUERIES),
        "mean_P@5": round(avg_p5, 3),
        "mean_MRR": round(avg_mrr, 3),
        "mean_NDCG@5": round(avg_ndcg5, 3),
        "mean_Recall": round(avg_recall, 3),
        "details": metrics_list
    }


if __name__ == "__main__":
    report = run_benchmark()
    print("Minesword Persian Benchmark Report:")
    print(f"Mean P@5: {report['mean_P@5']}")
    print(f"Mean MRR: {report['mean_MRR']}")
    print(f"Mean NDCG@5: {report['mean_NDCG@5']}")
    print(f"Mean Recall: {report['mean_Recall']}")
