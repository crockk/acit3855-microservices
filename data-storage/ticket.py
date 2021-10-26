from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from base import Base
import datetime


class Ticket(Base):
    """ Ticket """

    __tablename__ = "ticket"

    id = Column(Integer, primary_key=True)
    ticket_id= Column(Integer, nullable=False)
    ticket_holder = Column(String(250), nullable=False)
    purchase_date = Column(DateTime, nullable=True)
    contact = Column(String(250), nullable=True)
    show  = Column(Integer, nullable=False)
    date_created = Column(DateTime, nullable=True)

    def __init__(self, ticket_id, ticket_holder, purchase_date, contact, show):
        """ Initializes a ticket booking """
        self.ticket_id = ticket_id
        self.ticket_holder = ticket_holder
        self.purchase_date = purchase_date
        self.contact = contact
        self.show = show
        self.date_created = datetime.datetime.now() # Sets the date/time record is created


    def to_dict(self):
        """ Dictionary Representation of a ticket booking """
        dict = {}
        dict['id'] = self.id
        dict['ticket_id'] = self.ticket_id
        dict['ticket_holder'] = self.ticket_holder
        dict['purchase_date'] = self.purchase_date
        dict['contact'] = self.contact
        dict['show'] = self.show
        dict['date_created'] = self.date_created

        return dict
