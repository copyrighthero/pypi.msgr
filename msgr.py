# Author: Hansheng Zhao <copyrighthero@gmail.com> (https://www.zhs.me)

from multiprocessing import Queue
from sys import version_info
if version_info[0] == 2:
  from Queue import Empty
else:
  from queue import Empty


# import directive
__all__ = (
  '__author__', '__license__', '__version__',
  'MessageQueue', 'MessageBroker'
)
# package metadata
__author__ = 'Hansheng Zhao'
__license__ = 'BSD-2-Clause + MIT'
__version__ = '1.0.0'


class MessageQueue(object):
  """ MessageQueue class for queues """

  __slots__ = ('_queue', )

  def __init__(
    self, queue = None, messages = None, *args
  ):
    """
    MessageQueue class constructor
    :param queue: queue|None, queue instance
    :param messages: tuple|list|None, messages
    :param args: mixed, default messages
    """
    # initialize queue variable
    self._queue = Queue() \
      if queue is None else queue
    # initialize default values
    if messages:
      for item in messages: self.put(item)
    if args:
      for item in args: self.put(item)

  def __call__(
    self, message = None, *args, **kwargs
  ):
    """
    Alias for get & put a message to queue
    :param message: mixed|None, a message
    :param args: mixed, the arguments
    :param kwargs: dict, the kw arguments
    :return: None|mixed, a message
    """
    # check if message is set
    if message is None:
      # acquire a message
      return self.get(*args, **kwargs)
    else:
      # dispatch a message
      self.put(message, *args, **kwargs)

  def __getattr__(self, key):
    """
    Expose queue's attributes
    :param key: str, the attribute name
    :return: mixed, the queue properties
    """
    return self._queue.__getattribute__(key)

  def put(self, message, *args, **kwargs):
    """
    Put one message to queue with blocking
    :param message: mixed, a message
    :param args: mixed, the arguments
    :param kwargs: dict, the kw arguments
    :return: None
    """
    # put a message
    self._queue.put(message, *args, **kwargs)

  # aliases for put
  set = send = put

  def get(
    self,
    block = True, timeout = None,
    *args, **kwargs
  ):
    """
    Get one message from queue with blocking
    :param block: bool, whether block or not
    :param timeout, int|None, the timeout
    :param args: mixed, the arguments
    :param kwargs: dict, the kw arguments
    :return: mixed, a message
    """
    # check if blocking and empty
    if not block and self._queue.empty():
      return None
    # acquire a message
    try:
      message = self._queue.get(
        block, timeout, *args, **kwargs
      )
    except Empty:
      return None
    return message

  # aliases for get
  recv = get

  # alias for get & put message
  msg = property(get, put)


class MessageBroker(object):
  """ MessageBroker class for messages """

  __slots__ = (
    '_job', '_resolve', '_reject', '_service'
  )

  def __init__(
    self,
    job = None, res = None,
    rej = None, ser = None
  ):
    """
    MessageBroker class constructor
    :param job: message_queue|None, queue
    :param res: message_queue|None, queue
    :param rej: message_queue|None, queue
    :param ser: message_queue|None, queue
    """
    self._job = MessageQueue() \
      if job is None else job
    self._resolve = res
    self._reject = rej
    self._service = ser

  def __call__(
    self, message = None, *args, **kwargs
  ):
    """
    Alias for get & put a job to queue
    :param message: str, a message
    :param args: mixed, the arguments
    :param kwargs: dict, the kwargs
    :return: None|mixed, a message
    """
    # check if message is set
    if message is None:
      # acquire a message
      return self.acquire(*args, **kwargs)
    else:
      # dispatch a message
      self.dispatch(message, *args, **kwargs)

  def __getattr__(self, key):
    """
    Expose job queue's attributes.
    :param key: str, the attribute name
    :return: mixed, the attributes.
    """
    return self._job.__getattribute__(key)

  def acquire(
    self,
    block = True, timeout = None,
    *args, **kwargs
  ):
    """
    Acquire a message from job queue
    :param block: bool, whether wait or not
    :param timeout: numeric, wait time
    :param args: mixed, the arguments
    :param kwargs: dict, the kw arguments
    :return: mixed, a value
    """
    # acquire a message from job queue
    return self._job.get(
      block = block, timeout = timeout,
      *args, **kwargs
    )

  # aliases for acquire
  get = recv = acquire

  def dispatch(self, message, *args, **kwargs):
    """
    Dispatch a message to job queue
    :param message: mixed, a message
    :param args: mixed, the arguments
    :param kwargs: dict, the kw arguments
    :return: None
    """
    # dispatch a message to job queue
    self._job.put(message, *args, **kwargs)

  # aliases for dispatch
  set = put = send = dispatch

  def settle(
    self,
    block = False, timeout = 0, *args, **kwargs
  ):
    """
    Settle a succeeded result non-blocking
    :param block: bool, whether wait or not
    :param timeout: numeric, wait time
    :param args: mixed, the arguments
    :param kwargs: dict, the kw arguments
    :return: mixed, result object or None
    """
    # check if resolve queue is valid
    if self._resolve is None: return None
    # acquire a resolve message
    try:
      return self._resolve.get(
        block = block, timeout = timeout,
        *args, **kwargs
      )
    except Empty:
      return None

  def resolve(self, message, *args, **kwargs):
    """
    Dispatch a succeeded result
    :param message: mixed, a message
    :param args: mixed, the arguments
    :param kwargs: dict, the kw arguments
    :return: None
    """
    # dispatch a succeeded result to queue
    if self._resolve: self._resolve.put(
      message, *args, **kwargs
    )

  def handle(
    self,
    block = False, timeout = 0, *args, **kwargs
  ):
    """
    Handle a failed result non-blocking
    :param block: bool, whether wait or not
    :param timeout: numeric, wait for how long
    :param args: mixed, the arguments
    :param kwargs: dict, the kw arguments
    :return: mixed, result object or None
    """
    # check if resolve queue is valid
    if self._reject is None: return None
    # acquire a resolve message
    try:
      return self._reject.get(
        block = block, timeout = timeout,
        *args, **kwargs
      )
    except Empty:
      return None

  def reject(self, message, *args, **kwargs):
    """
    Dispatch a failed result
    :param message: mixed, a message
    :param args: mixed, the arguments
    :param kwargs: dict, the kw arguments
    :return: None
    """
    # dispatch a failed result to queue
    if self._reject: self._reject.put(
      message, *args, **kwargs
    )

  def inspect(
    self,
    block = False, timeout = 0, *args, **kwargs
  ):
    """
    Acquire a pair of results non-blocking
    :param block: bool, whether wait or not
    :param timeout: numeric, wait for how long
    :param args: mixed, the arguments
    :param kwargs: dict, the kw arguments
    :return: tuple(succeeded, failed), results
    """
    # acquire a pair of results
    return (
      self.settle(block, timeout, *args, **kwargs),
      self.handle(block, timeout, *args, **kwargs)
    )

  def conclude(
    self, resolve, reject, *args, **kwargs
  ):
    """
    Dispatch a pair of results
    :param resolve: mixed, a message
    :param reject: mixed, a message
    :param args: mixed, the arguments
    :param kwargs: dict, the kw arguments
    :return: None
    """
    self.resolve(resolve, *args, **kwargs)
    self.reject(reject, *args, **kwargs)

  def process(
    self,
    block = True, timeout = None, *args, **kwargs
  ):
    """
    Acquire a message from service queue
    :param block: bool, whether wait or not
    :param timeout: numeric, wait for how long
    :param args: mixed, the arguments
    :param kwargs: dict, the kw arguments
    :return: mixed, a value
    """
    # acquire a message from service queue
    return self._service.get(
      block, timeout, *args, **kwargs
    ) if self._service else None

  def request(self, message, *args, **kwargs):
    """
    Dispatch a service request
    :param message: mixed, a message
    :param args: mixed, the arguments
    :param kwargs: dict, the kw arguments
    :return: mixed, a value
    """
    # dispatch a service request
    if self._service: self._service.put(
      message, *args, **kwargs
    )

  # alias for get & put a message object
  msg = property(acquire, dispatch)
  # alias for get & put a message object
  job = property(acquire, dispatch)

  # alias for get a pair of results
  ram = property(inspect)

  # alias for get & put a success result
  res = property(settle, resolve)
  # alias for get & put a failed result
  rej = property(handle, reject)

  # alias for get & put service request
  ser = property(process, request)
