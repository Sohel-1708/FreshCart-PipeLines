"""Bonus integration scaffold. Complete and test on an actual broker and warehouse."""
from uuid import uuid4

def ingest_batch(fc, records):
    """fc is the authenticated elt.classroom_sql module; records are web-shaped orders.
    Caller must ensure pincode/customer/FX references already exist and ACK only
    after durable landing + successful load. Preserve order IDs on replay.
    """
    batch=uuid4().hex
    path=fc.write_landing('web',records,batch)
    fc.load_file(path,'bronze.orders_raw',f'bonus/{batch}')
    fc.query(f"SET run_id = '{batch}'")
    for sql in (fc.SQL_10_ORDERS_CLEAN,fc.SQL_20_ORDERS_DEDUP,fc.SQL_30_CUSTOMERS_SCD2,fc.SQL_31_FX_DAILY,fc.SQL_32_PINCODE_GEO,fc.SQL_40_GOLD):
        fc.run_sql(sql)
    return fc.query('SELECT COUNT(*),SUM(amount_inr),SUM(loyalty_points) FROM gold.fct_orders')[0]

# TODO(student): bind a dedicated FreshCart order exchange/queue; collect for 60s;
# validate body schema; persist batch; ACK on successful ingestion; replay exact
# same records and assert equal gold totals. Do not claim until actually tested.
