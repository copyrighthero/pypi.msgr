# Msgr Project #

[README中文文档](README.zh-CN.md)

## About the Msgr Library ##

懒，暂时还没翻译，不好意思哦...

The Msgr library provide two class: `MessageQueue` and `MessageBroker`.

The `MessageQueue` class is an easy to use inerface to queues like Python `queue`, `multiprocessing.Queue` or [Redistr](https://www.github.com/copyrighthero/Redistr)'s redis `Queue` interface. It is defaulted to use `multiprocessing.Queue` as its queue.

The `MessageBroker` class is a class that manages one to four queues -- `job`, `resolve`, `reject` and `service` queues respectively. The `job` queue is a must and is defaulted to a `MessageQueue` instance, the other three queues can be `None`. These queues can be changed when instantiating.

The `MessageQueue` is a thin wrapper around queue objects that has `put` and `get` methods, and the `MessageBroker` is the manager class for dispatching and receiving messages.

They can be used in `multiprocessing` environments for message passing between processes.

## How to Use Msgr Library ##

After installation using `pip install Msgr`, simply import and start coding :-)

```python
from msgr import MessageQueue, MessageBroker
from redis import Redis
from redistr import Queue

# create message queues
mqq = MessageQueue() # default, use `multiprocessing.Queue`
redis_queue = Queue(Redis(), 'queue_key') # create redistr Queue
redis_mqq = MessageQueue(redis_queue) # use redistr Queue instead

# most queue operations: put, get.
mqq.put({'test': 'case'})
mqq.get() # {'test': 'case'}
# `MessageQueue` exposes queue's properties
redis_mqq.length # 0, redistr queue's length property
# `MessageQueue` has msg property for convenience
redis_mqq.msg = 'test' # send a message, like `put('test')`
redis_mqq.msg = 'case'
redis_mqq.msg # 'test', get a message like `get()`
redis_mqq.msg # 'case'
# `MessageQueue` has __call__ method for put/get message
mqq('testcase') # send a message to queue
mqq() # 'testcase' # get a message from queue

# The MessageQueue is enough in most situations,
#   but if you want, the MessageBroker is here to help

# create message broker instance
#   default to use MessageQueue as its job queue, no resolve/reject/service queues
mb = MessageBroker()
#   change the job queue, resolve queue, reject queue or service queue
mb = MessageBroker(job = mqq, res = MessageQueue(), rej = redis_queue, ser = redis_mqq)

# dispath/acquire a job message
mb.dispatch('job message')
mb.acquire() # 'job message' received

# resolve a result, settle a resolved message
mb.resolve('job done')
mb.settle() # 'job done' received

# reject a result, handle a rejected message
mb.reject('job failed')
mb.handle() # 'job failed' received

# get or put a pair of resolve, reject messages
#   .inspect is non-blocking by default, can be changed to blocking
mb.conclude('resolve msg', 'reject msg')
mb.inspect() # ('resolve msg', 'reject msg') received.
mb.inspect() # (None, None)
mb.reject('failed')
mb.inspect() # (None, 'failed')

# request a service, process a service
mb.request('shutdown')
mb.process() # 'shutdown' received

# helper properties are provided
#   job queue properties, blocking
mb.msg = 'test'
mb.msg # 'test' received
mb.job = 'test'
mb.job # 'test' received
#   resolve queue property, blocking
mb.res = 'resolved'
mb.res # 'resolved' received
#   reject queue property, blocking
mb.rej = 'failed'
mb.rej # 'failed' received
#   service queue property, blocking
mb.ser = 'reboot'
mb.ser # 'reboot' received
#   inspect method property, non-blocking
mb.ram # (None, None) received
```

## Msgr Class API References ##

### `MessageQueue` Class ###

The thin wrapper for queues, exposes `put`, `set`, `send` for sending messages and `get`, `recv` for getting messages. It also exposes a `__call__` method and a `msg` property for sending/receiving messages. It also exposes all the queue properties for the user's conveniences.

Signature: `MessageQueue(queue = None, messages = None, *args)`

1. `queue` parameter: it takes in any instances that has `put` and `get` methods for sending and receiving messages, so it works with `queue`, `multiprocessing.Queue` and `redistr.Queue` objects. When nothing is passed in, it will use `multiprocessing.Queue` by default.

2. `messages` parameter: a iterable object should be passed in, all items in this iterable will be sent to the queue when instantiating.

3. `*args` parameter: any stray parameters will be considered as a message and will be sent to the queue.

- `put(message)`, `send(..)`, `set(..)` method: send a message to the queue.
- `get(block = True, timeout = 0)`, `recv(..)` method: get a message from queue, blocking operation, can pass in `block = False` to prevent blocking or `timeout = [second]` for changing block timeout.
- `__call__(message = None)`: if calling the instance directly without parameter, it will receive an message blocking; if the instance is called with one parameter, the parameter will be send to the queue.
- `msg` property: assignment to this property will send a message, simply accessing the property will get a message blocking.

### `MessageBroker` Class ###

The manager class for up to four queues of different usage. It takes four optional parameters: `job`, `res`, `rej` and `ser` corresponding to job queue, resolve queue, reject queue and service queue. By default if `job` queue is not passed in it will use `MessageQueue` as the job queue, which uses `multiprocessing.Queue` as its underlying queue.

The class also exposes different methods and properties for sending and receiving from different queues.

Signature: `MessageBroker(job = None, res = None, rej = None, ser = None)` 

1.2.3.4 `job`, `res`, `rej`, `ser` parameters: any queue instances, they can be the same but why do you want to do that?

- `__call__(message = None)` method: send/receive a job message to/from the job queue.
- `dispatch(message)`, `set(..)`, `put(..)`, `send(..)` method: send a job message.
- `acquire(block = True, timeout = 0)`, `get(..)`, `recv(..)` method: get a job message blocking.
- `resolve(message)` method: send a resolve (success) message to resolve queue.
- `settle(block = True, timeout = 0)` method: get a resolved message from resolve queue.
- `reject(message)` method: send a reject (fail) message to reject queue.
- `handle(block = True, timeout = 0)` method: get a rejected message from reject queue.
- `concude(resolve = None, reject = None)` method: send a pair of result messages as resolved and rejected msgs.
- `inspect(block = False, timeout = 0)` method: get a pair of result messages non-blocking.
- `request(message)` method: send a service request message.
- `process(block = True, timeout = 0)` method: get a service request message blocking.
- `msg`, `job` property: send/get a job message, blocking.
- `res` property: send/get a resolve message, blocking.
- `rej` property: send/get a reject message, blocking.
- `ser` property: send/get a service request message, blocking.
- `ram` property: get a pair of results from resolve queue and reject queue, non-blocking.
``
 

## Licenses ##

This project is licensed under two permissive licenses, please chose one or both of the licenses to your like. Although not necessary, bug reports or feature improvements, attributes to the author(s), information on how this program is used are welcome and appreciated :-) Happy coding 

[BSD-2-Clause License]

Copyright 2018 Hansheng Zhao

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

[MIT License]

Copyright 2018 Hansheng Zhao

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
