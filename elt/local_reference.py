"""Independent local calculation against the classroom fixture; not Snowflake."""
from decimal import Decimal
import re
from datetime import datetime
from elt.classroom_sql import MOCK_WEB_ORDERS, MOCK_MOBILE_ORDERS, MOCK_CRM_TIER_EVENTS, MOCK_FX_RESPONSES

def compute_baseline():
    rows = []
    for kind, records in [('web', MOCK_WEB_ORDERS), ('mobile', MOCK_MOBILE_ORDERS)]:
        for r in records:
            if kind == 'web':
                oid, email, ds, raw, cur, pin, stamp = (r[k] for k in ('order_id','cust_email','order_date','amount','currency','pincode','updated_at'))
            else:
                oid,email,ds,raw,cur,pin,stamp = r['orderId'],r['customer']['email'],r['orderDate'],r['total']['value'],r['total']['currency'],r['deliveryPin'],r['updatedAt']
            email=email.strip().lower();cur=cur.upper();amount=None if raw is None else Decimal(re.sub(r'[^0-9.-]','',str(raw)))
            for fmt in ('%Y-%m-%d','%d/%m/%Y','%b %d, %Y'):
                try: day=datetime.strptime(ds,fmt).date().isoformat();break
                except ValueError: pass
            reasons=[]
            if not re.fullmatch(r'[^@\s]+@[^@\s]+\.[a-z]{2,}',email):reasons.append('bad_email')
            if not re.fullmatch(r'[1-9][0-9]{5}',pin):reasons.append('bad_pincode')
            if amount is not None and amount<=0:reasons.append('non_positive_amount')
            rows.append(dict(order_id=oid,email=email,day=day,amount=amount,currency=cur,updated_at=datetime.fromisoformat(stamp),source=kind,reasons=reasons))
    clean=[r for r in rows if not r['reasons']];latest={}
    for r in clean:
        if r['order_id'] not in latest or r['updated_at']>=latest[r['order_id']]['updated_at']:latest[r['order_id']]=r
    gold=[]
    for oid,r in sorted(latest.items()):
        tier=max((v for v in MOCK_CRM_TIER_EVENTS if v['email']==r['email'] and v['effective_from']<=r['day']),key=lambda v:v['effective_from'])['tier']
        rate=Decimal('1') if r['currency']=='INR' else Decimal(str(MOCK_FX_RESPONSES[0]['rates'][r['day']]['INR']))
        amount=(r['amount']*rate).quantize(Decimal('.01'));pts=int(amount//100)*{'Silver':1,'Gold':2,'Platinum':3}[tier]
        gold.append(dict(order_id=oid,tier=tier,amount_inr=str(amount),loyalty_points=pts))
    summary={'bronze':len(rows),'clean':len(clean),'quarantine':len(rows)-len(clean),'dedup':len(gold),'revenue_inr':str(sum(Decimal(x['amount_inr']) for x in gold)),'points':sum(x['loyalty_points'] for x in gold),'rejected_percent':100*(len(rows)-len(clean))/len(rows)}
    return summary,gold

if __name__=='__main__':
    import json
    print(json.dumps(compute_baseline(), indent=2))
