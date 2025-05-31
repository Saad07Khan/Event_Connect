import connectDB from '../../../../lib/mongodb';
import Event from '../../../../models/Event';

export default async function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { id } = req.query;

  try {
    await connectDB();

    const event = await Event.findById(id);
    
    if (!event) {
      return res.status(404).json({ error: 'Event not found' });
    }

    // Return only necessary attendee information
    const attendees = event.attendees.map(attendee => ({
      name: attendee.name,
      mobileNumber: attendee.mobileNumber,
      joinedAt: attendee.joinedAt
    }));

    res.status(200).json(attendees);
  } catch (error) {
    console.error('Error fetching attendees:', error);
    res.status(500).json({ error: 'Error fetching attendees' });
  }
} 