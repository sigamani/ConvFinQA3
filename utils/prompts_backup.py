from langchain.prompts import PromptTemplate

generate_answer_and_program_prompt = PromptTemplate(
    template = '''
    You are a financial reasoning assistant. Your task is to read a user's natural language question and a structured table, then generate a precise answer using mathematical reasoning.
    
    First, interpret the table and extract any necessary numeric values.
    Then, write a short program-like expression in natural language that explains how to compute the answer.
    Finally, output a JSON object with two fields:
    
    - "program": a string showing the symbolic math operation (e.g., "subtract(60.94, 25.14), divide(#0, 25.14)")
    - "answer": the final computed value (rounded to 5 decimal places if needed)
    
    Only return the JSON. Do not include any additional text or commentary.
    
    ### Example Input
    Question: What is the percentage increase in exercise price from 2005 to 2007?
    Table:
    | Year | Price |
    |------|-------|
    | 2005 | 25.14 |
    | 2006 | 37.84 |
    | 2007 | 60.94 |
    
    ### Output
    {
      "program": "subtract(60.94, 25.14), divide(#0, 25.14)",
      "answer": 1.42403
    }
    
    ### New Input
    Question: {question}
    Table:
    {context}
    
    ### Output
    ''',
    input_variables=["question", "context"],
)


# Usage:
# normalized_prompt = normalize_facts_prompt.format(table_json=json.dumps(sample_table, indent=2))
normalize_facts_prompt = PromptTemplate(
    input_variables=["table_json"],
    template="""
        You are a financial document parser.

        You will receive a JSON object representing a table extracted from a financial report. The table is accompanied by `pre_text` and `post_text` — context paragraphs surrounding the table in the original document.

        Your task is to extract a list of normalized financial facts from the table.

        For each relevant cell in the table:
        - Determine the **type of metric** (e.g., Revenue, EPS, Margin, Assets) using column headers.
        - Extract the **numerical value**, and normalize it to **standard scientific notation** with 2 decimal places and 3 significant figures (e.g., "3.40E-1" for 0.34).
        - Infer the **unit** (e.g., USD, %, EPS, Billion) using the header or cell text.
        - Determine the **time** the value refers to. This is often encoded in row headers (e.g., “Q1”, “2020”, or “March 2021”).
        - Choose the most relevant sentence from `pre_text` or `post_text` that mentions or helps explain this value.

        Return a list of JSON objects. Each object should have the following fields:
        - "id": A unique identifier composed from the base "id" and row/column info (e.g., "ABC/2020/page_5.pdf-Row2-Revenue").
        - "type": The name of the metric (e.g., "Revenue").
        - "value": The value in scientific notation (e.g., "1.20E+9").
        - "unit": The unit associated (e.g., "USD").
        - "time": A universal date like "2020-01-01" or "2020-Q1".
        - "description": The best sentence from the context.

### Input JSON
        {table_json}

        Return only valid JSON.
        """
)



# Prompt
reason_and_answer_prompt_template = PromptTemplate(
    template="""You are an investment analyst. You will be given: 
    <INSTRUCTIONS>
        You will be provided:
        1. a QUESTION asked by the user
        2. CONTEXT provided by an automated context retrieval system
        
        Your task is to use the CONTEXT to provide a relevant ANSWER to the QUESTION.

        Only answer what the user is asking and nothing else.
        
        Explain your reasoning in a step-by-step manner. Ensure your reasoning and conclusion are correct.

        Avoid simply stating the correct answer at the outset.

        If there is no relevant context provided, state that at the outset.

        At the end of your calculations, provide a section for the final answer submission (must be in-between <ANSWER> and </ANSWER> tags).
    </INSTRUCTIONS>
    <EXAMPLE>
        <INPUT>
            <QUESTION>What is the percentage change in the net cash from operating activities from 2008 to 2009?</QUESTION>
            <CONTEXT>
            In 2008, the net cash from operating activities was $200,000.
            In 2009, the net cash from operating activities was $258,620.
            </CONTEXT>
        </INPUT>
        <OUTPUT>
            <REASONING>
                To calculate the percentage change, we can use the formula:


                Substituting the given values:

                old_value = 200000
                new_value = 258620

                percentage_change = ((258620 - 200000) / 200000) * 100

                percentage_change = (58620 / 200000) * 100

                percentage_change = 0.2931 * 100

                percentage_change = 29.31%

                Therefore, the percentage change in the net cash from operating activities from 2008 to 2009 is 29.31%.
            </REASONING>
            <ANSWER>29.31%</ANSWER>
        </OUTPUT>
    </EXAMPLE>
    <INPUT>
        <QUESTION>{question}</QUESTION>
        <CONTEXT>
        {context}
        </CONTEXT>
    </INPUT>
    """,
    input_variables=["question", "context"],
)


# Prompt
eval_prompt_template = PromptTemplate(
    template="""
    <INSTRUCTIONS>
        You are an evaluator for an algorithm that answers investment analyst questions.

        You will be provided:
        1. QUESTION: question asked by the user
        2. ACTUAL_ANSWER: answer generated by the algorithm
        3. EXPECTED_ANSWER: expected answer

        Your task is to evaluate the algorithm's provided answer based on how well it matches the expected answer.
        If needed, use the question to to inform your evaluation.
        
        Only provide a number between 0 and 1 for your evaluation and nothing else. DO NOT provide explanations.

        If the actual answer matches the expected answer exactly, provide 1.
        If the actual answer is close to the expected answer, provide a number between 0 and 1 based on how close it is.
        For numerical answers, you should use relative difference: 1 - ((abs(a - b) / max(abs(a), abs(b))) ** 2)
        If the actual answer is not close to the expected answer, provide 0.

        
    </INSTRUCTIONS>
    <EXAMPLE>
        <INPUT>
            <QUESTION>What is the percentage change in the net cash from operating activities from 2008 to 2009?</QUESTION>
            <ACTUAL_ANSWER>29.31</ACTUAL_ANSWER>
            <EXPECTED_ANSWER>25.42%</EXPECTED_ANSWER>
        </INPUT>
        <OUTPUT>
            0.87
        </OUTPUT>
    </EXAMPLE>
    <INPUT>
        <QUESTION>{question}</QUESTION>\n
        <ACTUAL_ANSWER>{actual_answer}</ACTUAL_ANSWER>\n
        <EXPECTED_ANSWER>{expected_answer}</EXPECTED_ANSWER>\n
    </INPUT>
    """,
    input_variables=["question", "actual_answer", "expected_answer"],
)


extract_anwer_prompt_template = PromptTemplate(
    template="""
    <INSTRUCTIONS>
        You will be provided:
        1. QUESTION: question asked by the user
        2. LONG ANSWER: reasoning steps, followed by a final answer

        Your task is to extract the SHORT ANSWER from the LONG ANSWER

        The short answer should be as concise as possible, while still answering the question.

        Only return the SHORT ANSWER and nothing else.

        If answer is not provided, say "NO ANSWER"
    </INSTRUCTIONS>
    <INPUT>
        <QUESTION>{question}</QUESTION>\n
        <LONG ANSWER>{generation}</LONG ANSWER>\n
    </INPUT>
    """,
    input_variables=["question", "generation"],
)

filter_context_prompt_template = PromptTemplate(
    template="""
    <INSTRUCTIONS>
        You will be provided:
        1. QUESTION: question asked by the user
        2. DOCUMENTS: list of retrieved documents

        Your task is to:
         - pick the relevant DOCUMENTS that can be used to answer the question
         - discard irrelevant DOCUMENTS that provide no useful information to answer the question
         - trim the relevant DOCUMENTS to only include the relevant information needed to answer the question

        Only return the relevant information from the documents and the source douments, nothing else.
        Return in a YAML like format (see example).
        Do not try to produce the answer, only provide the relevant information that should be used to answer the question.
        
    </INSTRUCTIONS>
    <EXAMPLE>
        <INPUT>
            <QUESTION>What is the percentage change in the net cash from operating activities from 2008 to 2009?</QUESTION>
            <DOCS>
                <DOC ID="some-relevant-doc-1">
                The net cash from operating activities in 2008 was $10 million.
                </DOC>
                <DOC ID="some-relevant-doc-2">
                The net cash from operating activities increased by $2 million in 2009.
                </DOC>
                <DOC ID="some-irrelevant-doc-1">
                The company's net revenue from sales in 2009 was $50 million, compared to $45 million in 2008.
                </DOC>
            </DOCS>        
        </INPUT>
        <OUTPUT>
            The net cash from operating activities in 2008 was $10 million.
            The net cash from operating activities increased by $2 million in 2009.
            
            sources:
                - some-relevant-doc-1
                - some-relevant-doc-2
        </OUTPUT>
    </EXAMPLE>
    <INPUT>
        <QUESTION>{question}</QUESTION>\n
        <DOCS>
        {documents}
        </DOCS>
    </INPUT>
    """,
    input_variables=["question", "documents"],
)


generate_queries_prompt_template = PromptTemplate.from_template(
    """Given this financial question, write 3 search queries that retrieve evidence to answer it.

Question: {question}

Queries:"""
)

