import connectDB from '../../../../lib/mongodb';
import Event from '../../../../models/Event';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { id } = req.query;
  const { name, mobileNumber } = req.body;

  if (!name || !mobileNumber) {
    return res.status(400).json({ error: 'Name and mobile number are required' });
  }

  if (!/^[0-9]{10}$/.test(mobileNumber)) {
    return res.status(400).json({ error: 'Please enter a valid 10-digit mobile number' });
  }

  try {
    await connectDB();

    // Find the event
    const event = await Event.findById(id);
    if (!event) {
      return res.status(404).json({ error: 'Event not found' });
    }

    // Check if user has already joined
    const existingAttendee = event.attendees?.find(
      attendee => attendee.mobileNumber === mobileNumber
    );

    if (existingAttendee) {
      return res.status(400).json({ error: 'You have already joined this event' });
    }

    // Add attendee
    const attendee = {
      name: name.trim(),
      mobileNumber: mobileNumber.trim(),
      joinedAt: new Date()
    };

    // Update the event with the new attendee
    event.attendees = [...(event.attendees || []), attendee];
    await event.save();

    res.status(200).json({ message: 'Successfully joined the event' });
  } catch (error) {
    console.error('Error joining event:', error);
    res.status(500).json({ error: 'Failed to join event. Please try again.' });
  }
}