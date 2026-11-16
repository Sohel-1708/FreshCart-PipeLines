"""Starter publisher; real broker execution pending."""
import argparse, json, os, random, time, uuid
from datetime import datetime, timezone
EXCHANGE='rapido-dispatch'
ZONES={'bangalore':['koramangala','indiranagar','whitefield'],'chennai':['tnagar','whitefield','adyar']}

def connect():
    import pika
    return pika.BlockingConnection(pika.URLParameters(os.getenv('AMQP_URL','amqp://guest:guest@127.0.0.1:5672/%2F')))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--count',type=int,default=60);parser.add_argument('--bad',action='store_true');args=parser.parse_args()
    conn=connect()
    try:
        ch=conn.channel();ch.exchange_declare(exchange=EXCHANGE,exchange_type='topic');ch.confirm_delivery()
        for i in range(1,args.count+1):
            city=random.choice(list(ZONES));zone=random.choice(ZONES[city]);kind=random.choice(['ride','food']);key=f'{city}.{zone}.{kind}'
            msg=dict(id=str(uuid.uuid4()),city=city,zone=zone,type=kind,ts=datetime.now(timezone.utc).isoformat())
            if args.bad and i%10==0:msg.pop('zone')
            ch.basic_publish(exchange=EXCHANGE,routing_key=key,body=json.dumps(msg));print('PUBLISHED',key,msg,flush=True);time.sleep(2)
    finally:conn.close()
if __name__=='__main__':main()
