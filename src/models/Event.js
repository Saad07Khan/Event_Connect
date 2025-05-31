import mongoose from 'mongoose';

const attendeeSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    trim: true
  },
  mobileNumber: {
    type: String,
    required: true,
    trim: true
  },
  joinedAt: {
    type: Date,
    default: Date.now
  }
}, { _id: false });

const eventSchema = new mongoose.Schema({
  title: {
    type: String,
    required: true,
    trim: true
  },
  description: {
    type: String,
    required: true,
    trim: true
  },
  summary: {
    type: String,
    trim: true
  },
  date: {
    type: Date,
    required: true
  },
  time: {
    type: String,
    required: true,
    trim: true
  },
  venue: {
    type: String,
    required: true,
    trim: true
  },
  registrationLink: {
    type: String,
    trim: true
  },
  attendees: {
    type: [attendeeSchema],
    default: []
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
}, { _id: true });

// Explicitly target the campusconnect database and events collection
const Event = mongoose.models.Event || mongoose.model('Event', eventSchema, 'events');

export default Event; 