# Memory Benchmark Report

## Configuration

| Field | Value |
|---|---|
| Benchmark version | 0.1.0 |
| Adapter | PiyAPIRestAdapter |
| Corpus hash | `` |
| Namespace | bench-micro-001 |
| top_k | 10 |
| Seed | n/a |
| Start | 2026-09-03T18:15:07Z |
| End | 2026-09-03T18:22:30Z |
| Platform |  |

## Summary

**Total cases:** 40  
**Passed:** 24  
**Failed:** 16  
**Overall pass rate:** 60.0%

## Scorecard by Category

| Category | Total | Passed | Failed | Pass Rate |
|---|---|---|---|---|
| abstention | 5 | 0 | 5 | 0.0% |
| alias | 14 | 14 | 0 | 100.0% |
| exact_duplicate | 10 | 10 | 0 | 100.0% |
| point_retrieval | 1 | 0 | 1 | 0.0% |
| semantic_duplicate | 2 | 0 | 2 | 0.0% |
| supersession | 6 | 0 | 6 | 0.0% |
| uncertainty | 2 | 0 | 2 | 0.0% |

## Component Metrics

### abstention

| Metric | Value |
|---|---|
| abstained | 0.000 |
| result_count | 10.000 |

### alias

| Metric | Value |
|---|---|
| alias_resolved | 1.000 |
| recall@10 | 0.379 |

### exact_duplicate

| Metric | Value |
|---|---|
| cluster_size | 25.700 |
| duplicates_in_results | 0.300 |
| top10_duplicate_ratio | 0.030 |

### point_retrieval

| Metric | Value |
|---|---|
| mrr | 0.000 |
| precision@5 | 0.000 |
| recall@10 | 0.000 |
| recall@5 | 0.000 |

### semantic_duplicate

| Metric | Value |
|---|---|
| original_found | 0.000 |
| paraphrase_found | 0.000 |

### supersession

### uncertainty

## Worst Failures (up to 20)

### `abstention_001` (abstention)

**Retrieved IDs (top 5):** ['42f19c44-fad6-41d6-ad19-d018168bfbd2', '035f1651-06bc-4b65-a466-2031ea4deea0', '3bad0242-078e-47be-a6b9-341f37e3ab30', '6c5a8213-4517-45a3-a8d8-b21e90720b72', '4d617707-f2d3-4d70-83dc-9874c5b2773d']

**note:** No memory records about favorite color exist
**Latency:** 13535ms

| Metric | Value |
|---|---|
| abstained | 0.000 |
| result_count | 10.000 |

### `abstention_002` (abstention)

**Retrieved IDs (top 5):** ['400a4556-c33e-4e2d-8684-ba8e3c6c89fc', '97369f50-e070-4923-84f1-918056d5257c', '4d617707-f2d3-4d70-83dc-9874c5b2773d', '6ccfe701-50a2-4792-967c-46759786f6cc', '035f1651-06bc-4b65-a466-2031ea4deea0']

**note:** Project Phoenix does not exist in the corpus
**Latency:** 12109ms

| Metric | Value |
|---|---|
| abstained | 0.000 |
| result_count | 10.000 |

### `abstention_003` (abstention)

**Retrieved IDs (top 5):** ['4d617707-f2d3-4d70-83dc-9874c5b2773d', '32750429-8bb8-4d9a-91af-c35fd0b14fae', '27f3d50e-dc59-4fd2-96d1-dd05bf6f89f1', '4e9b5f81-88ef-4e2f-9329-b5bca36779b7', 'd37c7bdf-f012-4f8b-8632-7de433743af7']

**note:** No salary information exists in the corpus
**Latency:** 12817ms

| Metric | Value |
|---|---|
| abstained | 0.000 |
| result_count | 10.000 |

### `abstention_004` (abstention)

**Retrieved IDs (top 5):** ['39b2d636-9b5a-41a1-abfa-5998b4796055', '54c122ca-d49a-4cec-9042-8aace9310123', '53e8930b-5394-411c-8e06-86d157b26194', 'a35e146e-78b0-4005-b002-d3c4549b27f0', 'da2150e3-9e48-4c5b-ba07-4f463efee9d8']

**note:** Acme Robotics appears as a project host but no founding info exists
**Latency:** 12071ms

| Metric | Value |
|---|---|
| abstained | 0.000 |
| result_count | 10.000 |

### `abstention_false_premise_001` (abstention)

**Retrieved IDs (top 5):** ['035f1651-06bc-4b65-a466-2031ea4deea0', '3bad0242-078e-47be-a6b9-341f37e3ab30', '42f19c44-fad6-41d6-ad19-d018168bfbd2', '6ccfe701-50a2-4792-967c-46759786f6cc', 'b2684157-927e-4d7c-89a4-8e58b76d4eca']

**note:** Morgan's latest language is Rust — the premise (switched away) is false
**Latency:** 11801ms

| Metric | Value |
|---|---|
| abstained | 0.000 |
| result_count | 10.000 |

### `retrieval_020` (point_retrieval)

**Retrieved IDs (top 5):** ['025944be-226b-47c9-8c91-9389b79a6076', '58298866-9042-41de-9c29-698bb71203f6', '1b2b0ac0-9754-477d-992f-5e9834046607', 'd83b3c86-3c66-40a9-84e2-3f82e4ff1066', '87452c1f-4591-418e-9222-9bf2ecd043ac']

**relevant_ids:** ['5181b982-c030-4ee1-8aaf-30cd4d647931']
**hits_in_top10:** []
**Latency:** 12157ms

| Metric | Value |
|---|---|
| mrr | 0.000 |
| precision@5 | 0.000 |
| recall@10 | 0.000 |
| recall@5 | 0.000 |

### `semantic_dup_003` (semantic_duplicate)

**Retrieved IDs (top 5):** ['f3b9edbd-8d8d-484c-8dec-9d15f4fa6191', '6618b39c-d1ea-48c6-ac2f-ed65bfcb349d', '30e4ee9d-83ce-4bd1-8970-266502b37112', '9dbf724e-2eea-4ff9-9c6f-82502a4560b5', 'ac040988-0191-4eaa-a762-9af5d92e172f']

**paraphrase_text:** Paraphrased recollection: Casey Monroe bought a refurbished laptop for testing Juniper.
**original_text:** Casey Monroe bought a refurbished laptop for testing Juniper.
**Latency:** 12430ms

| Metric | Value |
|---|---|
| original_found | 0.000 |
| paraphrase_found | 0.000 |

### `semantic_dup_007` (semantic_duplicate)

**Error:** The read operation timed out

**Retrieved IDs (top 5):** []


### `supersession_morgan_vale_preferred_database` (supersession)

**Error:** <urlopen error [Errno 8] nodename nor servname provided, or not known>

**Retrieved IDs (top 5):** []


### `supersession_morgan_vale_preferred_language` (supersession)

**Error:** <urlopen error [Errno 8] nodename nor servname provided, or not known>

**Retrieved IDs (top 5):** []


### `supersession_morgan_vale_work_city` (supersession)

**Error:** <urlopen error [Errno 8] nodename nor servname provided, or not known>

**Retrieved IDs (top 5):** []


### `supersession_morgan_vale_meeting_preference` (supersession)

**Error:** <urlopen error [Errno 8] nodename nor servname provided, or not known>

**Retrieved IDs (top 5):** []


### `supersession_morgan_vale_morning_drink` (supersession)

**Error:** <urlopen error [Errno 8] nodename nor servname provided, or not known>

**Retrieved IDs (top 5):** []


### `supersession_morgan_vale_preferred_editor` (supersession)

**Error:** <urlopen error [Errno 8] nodename nor servname provided, or not known>

**Retrieved IDs (top 5):** []


### `uncertainty_000` (uncertainty)

**Error:** <urlopen error [Errno 8] nodename nor servname provided, or not known>

**Retrieved IDs (top 5):** []


### `uncertainty_004` (uncertainty)

**Error:** <urlopen error [Errno 8] nodename nor servname provided, or not known>

**Retrieved IDs (top 5):** []


## Latency Summary

| Stat | ms |
|---|---|
| min | 11759 |
| median | 12241 |
| p95 | 13499 |
| max | 13535 |
| mean | 12276 |
