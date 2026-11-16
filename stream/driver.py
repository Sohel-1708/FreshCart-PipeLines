"""Starter private-queue subscriber; real broker execution pending."""
import argparse,json
if __package__:
    from stream.dispatcher import connect,EXCHANGE
else:
    from dispatcher import connect,EXCHANGE

def main():
    p=argparse.ArgumentParser();p.add_argument('name');p.add_argument('pattern');args=p.parse_args()
    conn=connect()
    try:
        ch=conn.channel();ch.exchange_declare(exchange=EXCHANGE,exchange_type='topic');queue=ch.queue_declare(queue='',exclusive=True).method.queue
        ch.queue_bind(exchange=EXCHANGE,queue=queue,routing_key=args.pattern);ch.basic_qos(prefetch_count=1)
        def receive(channel,method,properties,body):
            try: msg=json.loads(body);valid=isinstance(msg,dict) and 'zone' in msg
            except (ValueError,TypeError): msg={};valid=False
            if valid:
                print(args.name,'ACK',method.routing_key,msg,flush=True);channel.basic_ack(delivery_tag=method.delivery_tag)
            else:
                print(args.name,'NACK',method.routing_key,msg,flush=True);channel.basic_nack(delivery_tag=method.delivery_tag,requeue=False)
        ch.basic_consume(queue=queue,on_message_callback=receive,auto_ack=False);print(args.name,'READY',args.pattern,flush=True);ch.start_consuming()
    except KeyboardInterrupt: pass
    finally:
        if conn.is_open:conn.close()
if __name__=='__main__':main()
