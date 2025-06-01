import connectDB from '@/lib/mongodb';
import Event from '@/models/Event';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    await connectDB();
    
    // Find all events with malformed registration links
    const events = await Event.find({
      registrationLink: { $regex: /Registration$/, $options: 'i' }
    });

    // Fix each event's registration link
    for (const event of events) {
      // Remove the word "Registration" from the end of the link
      const fixedLink = event.registrationLink.replace(/Registration$/, '').trim();
      
      // Update the event with the fixed link
      await Event.findByIdAndUpdate(event._id, {
        registrationLink: fixedLink
      });
    }

    res.status(200).json({ 
      message: 'Successfully fixed registration links',
      fixedCount: events.length
    });
  } catch (error) {
    console.error('Error fixing registration links:', error);
    res.status(500).json({ error: 'Error fixing registration links' });
  }
} 