import { getSession } from 'next-auth/react';
import connectDB from '../../../lib/mongodb';
import Event from '../../../models/Event';

export default async function handler(req, res) {
  if (req.method === 'GET') {
    try {
      await connectDB();
      const events = await Event.find().sort({ date: 1 });
      res.status(200).json(events);
    } catch (error) {
      console.error('Error fetching events:', error);
      res.status(500).json({ error: 'Error fetching events' });
    }
  } else if (req.method === 'POST') {
    const session = await getSession({ req });

    if (!session) {
      return res.status(401).json({ error: 'Unauthorized' });
    }

    try {
      await connectDB();
      const { title, description, date, time, venue, registrationLink } = req.body;

      const event = new Event({
        title,
        description,
        date,
        time,
        venue,
        registrationLink,
      });

      await event.save();
      res.status(201).json(event);
    } catch (error) {
      console.error('Error creating event:', error);
      res.status(500).json({ error: 'Error creating event' });
    }
  } else {
    res.status(405).json({ error: 'Method not allowed' });
  }
} 