from src.ingestion.loader import load_all_cases

from src.graph.citation_graph import CitationGraph

from src.graph.citation_resolver import CitationResolver

from src.retrieval.chunk_search import (
    ChunkSearchEngine
)

from src.llm.llm_query_parser import (
    LLMQueryParser
)

#from src.query.query_parser import (
#        parse_query
#)


cases = load_all_cases("data/raw")

print(f"Loaded {len(cases)} cases")


#citation_graph = CitationGraph()
#
#for case in cases:
#    citation_graph.add_case(case)


resolver = CitationResolver(cases)

citation_graph = CitationGraph(resolver=resolver)

search_engine = ChunkSearchEngine(cases, citation_graph=citation_graph)

query_parser = LLMQueryParser()

for case in cases:
    citation_graph.add_case(case)

#Testing citation graph 
#sample_case = cases[0]
#print(sample_case.title)
#
#print(
#    citation_graph.get_cited_cases(
#        sample_case.case_id
#    )[:5]
#)
#
#print(
#    citation_graph.citation_count(
#        sample_case.case_id
#    )
#)

#Testing citation resolver
#sample_case = cases[0]
#
#print(
#    citation_graph.get_cited_cases(
#        sample_case.case_id
#    )
#)
#
#print(
#    citation_graph.get_citing_cases(
#        sample_case.case_id
#    )
#)
#
#print(
#    citation_graph.citation_count(
#        sample_case.case_id
#    )
#)

while True:

    query = input("\nEnter query: ")

    if query.lower() == "exit":
        break



    court_input = input(
    "Court filter (optional): "
    ).strip()

    if query.lower() == "exit":
        break

    jurisdiction_input = input(
        "Jurisdiction filter (optional): "
    ).strip()

    if query.lower() == "exit":
        break

    judge_input = input(
        "Judge filter (optional): "
    ).strip()

    if query.lower() == "exit":
        break

    category_input = input(
        "Category filter (optional): "
    ).strip()

    if query.lower() == "exit":
        break

    parsed = query_parser.parse_query(query)

    court = (
        court_input
        if court_input
        else parsed.get("court")
    )

    jurisdiction = (
        jurisdiction_input
        if jurisdiction_input
        else parsed.get("jurisdiction")
    )

    judge = (
        judge_input
        if judge_input
        else parsed.get("judge")
    )

    category = (
        category_input
        if category_input
        else parsed.get("category")
    )
    print("\nInput Components:")

    print("\nQuery:")
    print(parsed.get("semantic_query", query))

    print(f"\nCourt:")
    print(court)

    print(f"\nJurisdiction:")
    print(jurisdiction)

    print(f"\nJudge:")
    print(judge)

    print(f"\nCategory:")
    print(category_input)

    print("\nRetriveing Cases... Wait a moment...")

    search_output = search_engine.search(
        query=parsed["semantic_query"],
        court=court,
        jurisdiction=jurisdiction,
        judge=judge,
        category=category

    )

    results = search_output["results"]
    answer = search_output["answer"]

    print("\nSYNTHESIZED LEGAL ANSWER:\n")
    print(answer)

    print("\nTop Results:\n")

    for i, result in enumerate(results, start=1):

        chunk = result["chunk"]

        print(f"\n{i}. {chunk.case_title}")

        print(f"\nCase_id: {chunk.case_id}")

        print(f"\nCourt: {chunk.court}")

        print(f"\nJurisdiction: {chunk.jurisdiction}")

        print(f"\nJudge: {chunk.judges}")

        print(
        "\nCategory:",
        result["chunk"].legal_category)

       # print(
       # "Citation Score:",
       # result["citation_score"])

        print(f"\nScore: {result['score']}")

        print()

        #print("\nENTITIES:")
        #print(result["entities"])

        print("SUMMARY:")
        print(result["summary"])

        print("\nLEGAL ISSUE:")
        print(result["legal_issue"])

        print("\nREASONING:")
        print(result["reasoning"])

        print("\nHOLDING:")
        print(result["holding"])

        print("\nPROCEDURAL POSTURE:")
        print(result["procedural_posture"])


        print("\n" + "="*80 + "\n")
