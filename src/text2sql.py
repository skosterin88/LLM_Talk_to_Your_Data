from langchain_community.utilities import SQLDatabase
import re
from langchain_ollama import ChatOllama

def init_llm(model_name: str = "mistral", verbose: bool = False) -> ChatOllama:
    llm = ChatOllama(model=model_name, verbose=verbose)
    return llm

def get_langchain_response(question: str, db: SQLDatabase, llm: ChatOllama, verbose=False) -> str:
    
    direct_prompt = f"""
    Given an input question, create a syntactically correct SQL query to
    run in DuckDB. The database is defined by the following schema:

    {db.get_table_info()}

    Only use the following tables:
    {db.get_usable_table_names()}

    Pay attention to use only the column names you can see in the tables
    below. Be careful to not query for columns that do not exist. Also, pay
    attention to which column is in which table. Please carefully think
    before you answer.
    Make sure to use proper SQL syntax.
    Make sure to use double quotes for table names and single quotes for string values.
    Make sure to use proper date formats.
    Make sure to only query for data that exists in the database.
    Only generate a single SQL query as your answer.
    Make sure the query returns the answer to the question.
    Make sure the SQL query is syntactically correct.
    Make sure that you use proper aggregation functions if needed.
    Make sure to use aliases if needed.
    Make sure to use GROUP BY if needed.
    Make sure to use JOINs if needed.
    Don't provide any comments in the SQL query.

    Question: 
    """

    response = llm.invoke(direct_prompt + question)

    if verbose:
        print(response)

    print(re.search("(SELECT.*);", response.content.replace("\n", " ")).group(1))
    print(
        db.run(re.search("(SELECT.*);", response.content.replace("\n", " ")).group(1))
    )
    
    query = re.search("(SELECT.*);", response.content.replace("\n", " ")).group(1)
    result = db.run(query)
    
    return query, result