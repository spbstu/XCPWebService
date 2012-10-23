from soaplib.core.model.clazz import ClassModel, Array
from soaplib.core.model.primitive import String, Boolean

class StatusVLAB(ClassModel):
    __namespace__ = "http://devel.avalon.ru/"

    StatusOK    = Boolean
    Messages    = Array(String)

class PropertyConf(ClassModel):
    __namespace__ = "http://devel.avalon.ru/"

    Ref         = String
    Value       = String


class ConfigLab(ClassModel):
    __namespace__ = "http://devel.avalon.ru/"

    Action      = String
    Users       = Array(String)
    NameLab     = String

class ValueXCP(ClassModel):
    __namespace__ = "http://devel.avalon.ru/"

    Ref         = String
    Value       = String

class ValuesXCP(ClassModel):
    __namespace__ = "http://devel.avalon.ru/"

    Status      = StatusVLAB
    Values      = Array(ValueXCP)

class SingleValueXCP(ClassModel):
    __namespace__ = "http://devel.avalon.ru/"

    Status      = StatusVLAB
    Values      = String

class ValuesAD(ClassModel):
    __namespace__ = "http://devel.avalon.ru/"

    Status      = StatusVLAB
    Values      = Array(String)