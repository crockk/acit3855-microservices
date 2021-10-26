from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from base import Base
import datetime


class Show(Base):
    """ show """

    __tablename__ = "show"

    id = Column(Integer, primary_key=True)
    show_id = Column(Integer, nullable=False)
    artist = Column(String(250), nullable=False)
    showtime = Column(DateTime, nullable=False)
    venue = Column(String(250), nullable=False)
    available_tickets = Column(Integer, nullable=False)
    booking_contact = Column(String(250), nullable=True)
    date_created = Column(DateTime, nullable=True)

    def __init__(self, show_id, artist, showtime, venue, available_tickets, booking_contact):
        """ Initializes a show booking """
        self.show_id = show_id
        self.artist = artist
        self.showtime = showtime
        self.venue = venue
        self.available_tickets = available_tickets
        self.booking_contact = booking_contact
        self.date_created = datetime.datetime.now() # Sets the date/time record is created


    def to_dict(self):
        """ Dictionary Representation of a show booking """
        dict = {}
        dict['id'] = self.id
        dict['show_id'] = self.show_id
        dict['artist'] = self.artist
        dict['showtime'] = self.showtime
        dict['venue'] = self.venue
        dict['available_tickets'] = self.available_tickets
        dict['booking_contact'] = self.booking_contact
        dict['date_created'] = self.date_created

        return dict
