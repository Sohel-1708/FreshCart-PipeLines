# Environment setup
- Python 3.12+ recommended; create a venv and run pip install -r requirements.txt.
- Copy .env.example to .env locally with valid credentials (never commit .env).
- Run notebooks from project root; execute live services (Snowflake/Mage/RabbitMQ) in configured environments.# Bonus setup (documented)
- stream/lakehouse_consumer.py provides the ingestion scaffold for streaming orders into Snowflake gold tables.
- Configure AMQP_URL and Snowflake credentials in a local .env (not committed); run dispatcher/driver and consumer in a configured environment to verify end-to-end.
- A3 evidence and full bonus execution remain pending verified live runs in this workspace.
