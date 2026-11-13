# SQLPilot – AI-Powered SQL Assistant

**Ask questions about your database in natural language. SQLPilot converts them into SQL, executes them securely through an MCP server, and returns meaningful results.**

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey)
![MCP](https://img.shields.io/badge/Protocol-Model_Context_Protocol-purple)
![LLM](https://img.shields.io/badge/LLM-Ollama-orange)

## Overview

SQLPilot is an AI-powered SQL assistant that allows users to interact with relational databases using natural-language questions instead of manually writing SQL queries.

It uses a locally hosted Large Language Model (LLM) through Ollama to dynamically generate SQL queries based on the database schema. The generated queries are validated and executed through a custom Model Context Protocol (MCP) server.

SQLPilot also supports conversational memory, allowing users to ask follow-up questions without repeatedly specifying the entities or context.

## Key Features

- **Natural Language to SQL:** Converts natural-language questions into dynamically generated SQL queries.
- **Dynamic SQL Generation:** Generates queries based on the actual database schema instead of relying on predefined query templates.
- **MCP Server Integration:** Uses a custom MCP server to expose database schema inspection and query execution capabilities.
- **SQL Validation:** Uses SQLGlot to parse and validate queries, restricting execution to read-only SQL operations.
- **Conversational Memory:** Maintains recent conversation history to understand follow-up questions and contextual references.
- **Local LLM Integration:** Uses Ollama with the Qwen3:4B model for local SQL generation.
- **Relational Database Support:** Demonstrates multi-table JOINs, aggregations, filtering, sorting, and ranking using SQLite.
- **Structured Results:** Displays database query results in a readable format.

## Architecture

```text
                 User
                  |
                  v
        Natural Language Question
                  |
                  v
       Conversation Memory
                  |
                  v
       Ollama (Qwen3:4B)
          Dynamic SQL
          Generation
                  |
                  v
          SQL Validation
             SQLGlot
                  |
                  v
          MCP Client
                  |
                  v
          MCP Server
                  |
                  v
          SQLAlchemy
                  |
                  v
           SQLite DB
                  |
                  v
          Query Results
                  |
                  v
       Python Result Formatter
                  |
                  v
              User
```

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application development |
| Ollama | Local LLM execution |
| Qwen3:4B | Natural-language-to-SQL generation |
| Model Context Protocol (MCP) | Communication between AI client and database tools |
| SQLite | Relational database |
| SQLAlchemy | Database connectivity and inspection |
| SQLGlot | SQL parsing and validation |
| python-dotenv | Environment configuration |

## Project Structure

```text
sqlmcp/
│
├── database/
│   └── sqlpilot.db
│
├── prompts/
│
├── resources/
│
├── security/
│   └── sql_validator.py
│
├── tests/
│
├── tools/
│
├── .env.example
├── .gitignore
│
├── conversation_memory.py
├── database.py
├── db_engine.py
├── llm_client.py
├── requirements.txt
├── schema_inspector.py
└── server.py
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/SQLPilot.git
cd SQLPilot
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

**Windows:**

```powershell
.venv\Scripts\activate
```

**Linux / macOS:**

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Ollama

Download and install Ollama:

https://ollama.com/

Pull the Qwen3:4B model:

```bash
ollama pull qwen3:4b
```

### 5. Configure environment variables

Create a `.env` file in the project root:

```env
DATABASE_URL=sqlite:///database/sqlpilot.db
OLLAMA_MODEL=qwen3:4b
```

Refer to `.env.example` for the required configuration.

### 6. Initialize the database

Run the database initialization script:

```bash
python database.py
```

This creates the SQLite database and populates it with sample e-commerce data.

### 7. Run SQLPilot

Start the application:

```bash
python llm_client.py
```

The application connects to the MCP server, retrieves the database schema, and initializes the conversational assistant.

## Example Usage

SQLPilot supports natural-language questions and contextual follow-ups.

**Example 1 – Customer filtering**

```text
You: Show all customers from Kochi.
```

Generated SQL:

```sql
SELECT name
FROM customers
WHERE city = 'Kochi';
```

**Example 2 – Aggregation and ranking**

```text
You: Which customer spent the most?
```

Generated SQL:

```sql
SELECT
    customers.name,
    SUM(order_items.quantity * order_items.unit_price)
        AS total_spent
FROM customers
JOIN orders
    ON customers.customer_id = orders.customer_id
JOIN order_items
    ON orders.order_id = order_items.order_id
GROUP BY customers.customer_id
ORDER BY total_spent DESC
LIMIT 1;
```

**Example 3 – Conversational follow-up**

```text
You: Which customer spent the most?

SQLPilot: Ahmed spent the most, with a total of 73100.

You: What are his orders?

SQLPilot: Displays Ahmed's orders.

You: Name the products he bought.

SQLPilot: Displays the products purchased by Ahmed.

You: Where is he from?

SQLPilot: Kochi.
```

The assistant uses previous questions and query results to resolve contextual references such as "his" and "he".

## Database Schema

The project uses a sample e-commerce database containing four relational tables.

| Table | Description |
|---|---|
| customers | Customer information |
| products | Product details and prices |
| orders | Customer order information |
| order_items | Products and quantities associated with orders |

Relationships:

- `customers.customer_id` → `orders.customer_id`
- `orders.order_id` → `order_items.order_id`
- `products.product_id` → `order_items.product_id`

## Security

SQLPilot includes initial read-only SQL safeguards:

- SQLGlot-based SQL parsing and validation.
- Restriction to SELECT-style queries.
- SQLite read-only query configuration through `PRAGMA query_only`.
- MCP-side validation before query execution.

**Note:** These are foundational safeguards, not a complete production-grade database security solution. Additional controls such as query timeouts, resource limits, access restrictions, and stronger isolation are important before deployment.

## Current Limitations

- Conversational memory is currently maintained in application memory and does not persist across restarts.
- SQL generation quality depends on the LLM and the clarity of user questions.
- The current implementation uses SQLite.
- The application is designed as a local assistant rather than a production multi-user service.

## Future Improvements

- Persistent conversational memory using SQLite.
- Improved SQL generation and query optimization.
- Query execution timeouts and additional security controls.
- Support for additional relational databases such as PostgreSQL and MySQL.
- Better result visualization and reporting.
- Automated evaluation of SQL generation accuracy.
- Improved handling of ambiguous questions and conversational context.

## Author

**Ahmed**

Developed as a project exploring Large Language Models, Model Context Protocol, dynamic SQL generation, and conversational AI.

---

If you find this project interesting, feel free to explore the repository and suggest improvements!
