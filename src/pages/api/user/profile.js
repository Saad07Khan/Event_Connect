import { getSession } from 'next-auth/react';
import connectDB from '../../../lib/mongodb';
import User from '../../../models/User';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const session = await getSession({ req });
  if (!session) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  try {
    await connectDB();

    const { name, mobileNumber, branch, year } = req.body;

    // Validate mobile number
    if (!/^[0-9]{10}$/.test(mobileNumber)) {
      return res.status(400).json({ error: 'Invalid mobile number' });
    }

    // Update or create user profile
    const user = await User.findOneAndUpdate(
      { email: session.user.email },
      {
        name,
        mobileNumber,
        branch,
        year,
        email: session.user.email,
        image: session.user.image
      },
      { upsert: true, new: true }
    );

    res.status(200).json(user);
  } catch (error) {
    console.error('Error updating profile:', error);
    res.status(500).json({ error: 'Error updating profile' });
  }
} 