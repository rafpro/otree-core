from django.http import HttpResponseRedirect
from django.db import models
import common
from common import Symbols
from urlparse import urljoin
from django.conf import settings

class BaseTreatment(models.Model):
    """
    Base class for all Treatments.
    Example of a treatment:
    'dictator game with stakes of $1, where participants have to chat with each other first'
    It's the definition of what everyone in the treatment group has to do.
    A treatment is defined before the experiment starts.
    Results of a game are not stored in ther Treatment object, they are stored in Match or Participant objects.
    """

    description = models.TextField(max_length = 1000, null = True, blank = True)

    # the treatment code in the URL. This is generated automatically.
    # we don't use the primary key because a user might try incrementing/decrementing it out of curiosity/malice,
    # and end up in the wrong treatment
    code = common.RandomCharField(length=8)
        
    base_pay = models.PositiveIntegerField() # how much people are getting paid to perform it

    randomization_weight = models.FloatField(default = 1.0)

    participants_per_match = None

    def start_url(self):
        """The URL that a user is redirected to in order to start a treatment"""
        return urljoin(settings.DOMAIN,
                       '/{}/GetTreatmentOrParticipant/?{}={}&{}={}'.format(self.experiment.url_base,
                                                          Symbols.treatment_code,
                                                          self.code,
                                                          Symbols.demo_code,
                                                          self.experiment.demo_code))

    def __unicode__(self):
        s = self.code
        if self.description:
            s += ' ({})'.format(self.description)
        return s

    def matches(self):
        """Syntactic sugar"""
        return self.match_set.all()

    #@abc.abstractmethod
    def sequence(self):
        """
        Returns a list of all the View classes that the user gets routed through sequentially.
        (Not all pages have to be displayed for all participants; see the is_displayed method)
        
        Example:
        import donation.views as views
        import ptree.views.concrete
        return [views.Start,
                ptree.views.concrete.AssignParticipantAndMatch,
                views.IntroPage,
                views.EnterOfferEncrypted, 
                views.ExplainRandomizationDetails, 
                views.EnterDecryptionKey,
                views.NotifyOfInvalidEncryptedDonation,
                views.EnterOfferUnencrypted,
                views.NotifyOfShred,
                views.Survey,
                views.RedemptionCode]

        """
        raise NotImplementedError()

    def sequence_as_urls(self):
        """Converts the sequence to URLs.

        e.g.:
        sequence() returns something like [views.IntroPage, ...]
        sequence_as_urls() returns something like ['mygame/IntroPage', ...]
        """
        return [View.url(index) for index, View in enumerate(self.sequence())]

    class Meta:
        abstract = True
