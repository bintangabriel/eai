class GpuAvail:
  _instance = None
  gpu = []

  def __new__(cls, *args, **kwargs):
    if not cls._instance:
      cls._instance = super(GpuAvail, cls).__new__(cls, *args, **kwargs)
    return cls._instance

  @classmethod
  def get_gpu(cls):
    return cls.gpu

  @classmethod
  def set_gpu(cls, gpu):
    cls.gpu = gpu
    return cls.gpu
