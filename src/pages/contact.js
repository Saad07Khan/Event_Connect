import { useState } from 'react';

export default function Contact() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    message: ''
  });
  const [status, setStatus] = useState({
    loading: false,
    error: null,
    success: false
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus({ loading: true, error: null, success: false });

    try {
      const response = await fetch('/api/contact', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Something went wrong');
      }

      setStatus({ loading: false, error: null, success: true });
      setFormData({ name: '', email: '', message: '' }); // Reset form
    } catch (error) {
      setStatus({ loading: false, error: error.message, success: false });
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  return (
    <div>
      <div className="flex flex-col items-center justify-center py-12">
        <h1 className="text-3xl font-bold text-white mb-4">We'd love to hear from you!</h1>
        <p className="text-lg text-white text-center mb-8 px-4">Any queries, any suggestions? Please contact us.</p>

        <div className="w-full max-w-md bg-black p-8 rounded-lg shadow-md">
          {status.success && (
            <div className="mb-4 p-4 bg-green-100 text-green-700 rounded-md">
              Thank you for your message! We'll get back to you soon.
            </div>
          )}
          
          {status.error && (
            <div className="mb-4 p-4 bg-red-100 text-red-700 rounded-md">
              {status.error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label htmlFor="name" className="block text-white text-sm font-bold mb-2 uppercase">Name</label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                className="w-full py-2 px-3 text-white bg-transparent border-b border-white focus:outline-none"
                required
              />
            </div>
            <div className="mb-4">
              <label htmlFor="email" className="block text-white text-sm font-bold mb-2 uppercase">Email</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="w-full py-2 px-3 text-white bg-transparent border-b border-white focus:outline-none"
                required
              />
            </div>
            <div className="mb-6">
              <label htmlFor="message" className="block text-white text-sm font-bold mb-2 uppercase">Message</label>
              <textarea
                id="message"
                name="message"
                value={formData.message}
                onChange={handleChange}
                rows="4"
                className="w-full py-2 px-3 text-white bg-transparent border-b border-white focus:outline-none"
                required
              ></textarea>
            </div>
            <div className="flex items-center justify-between mt-8">
              <button
                type="submit"
                disabled={status.loading}
                className="w-full bg-black text-white font-bold py-3 px-4 rounded focus:outline-none focus:shadow-outline hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {status.loading ? 'Sending...' : 'Send Message'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
} 