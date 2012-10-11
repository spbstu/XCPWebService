__author__ = 'artzab'

class BaseMethods(object):

    @property
    def logging(self): return self._logging
    @logging.setter
    def logging(self, value): self._logging = value

    @property
    def config(self): return self._config
    @config.setter
    def config(self, value): self._config = value

    def __init__(self, logging=None, conf=None):
        self.logging = logging
        self.config = conf


    def messages(self,type="DEBUG",mesg="FOOOOO", error=False):
        if error and self.logging:
            self.logging.Messages.append('%s: %s' % (type, mesg))
            self.logging.StatusOK = False
        elif error:
            print ('%s: %s' % (type, mesg))
        elif self.config and self._logging:
            if self.config['debug']:
                self.logging.Messages.append('%s: %s' % (type, mesg))
        elif self.config:
            if self.config['debug']:
                print ('%s: %s' % (type, mesg))
