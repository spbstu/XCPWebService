from soaplib.core.model.clazz import ClassModel, Array
from soaplib.core.model.primitive import String, Boolean

class StatusVLAB(ClassModel):
    __namespace__ = "http://devel.avalon.ru/VLABManager/vars"

    StatusOK    = Boolean
    Messages    = Array(String)

class PropertyConf(ClassModel):
    __namespace__ = "http://devel.avalon.ru/VLABManager/vars"

    Ref         = String
    Value       = String

class VMConf(ClassModel):
    __namespace__ = "http://devel.avalon.ru/VLABManager/vars"

    Template    = PropertyConf
    Folder      = String
    Suffix      = String
    Tags        = Array(String)
    Networks    = Array(PropertyConf)


class ConfigLab(ClassModel):
    __namespace__ = "http://devel.avalon.ru/VLABManager/vars"

    Action      = String
    PoolName    = String
    DomainKrb   = String
    Users       = Array(String)
    VMs         = Array(VMConf)

class ValueXCP(ClassModel):
    __namespace__ = "http://devel.avalon.ru/VLABManager/vars"

    Ref         = String
    Value       = String

class ValuesXCP(ClassModel):
    __namespace__ = "http://devel.avalon.ru/VLABManager/vars"

    Status      = StatusVLAB
    Values      = Array(ValueXCP)

class ValuesAD(ClassModel):
    __namespace__ = "http://devel.avalon.ru/VLABManager/vars"

    Status      = StatusVLAB
    Values      = Array(String)