// components/Layout.js
import Link from 'next/link';
import Image from 'next/image';

export default function Layout({ children }) {
  return (
    <div className="min-h-screen bg-gray-50 relative">
      {/* Background Image */}
      <div 
        className="fixed inset-0 z-0"
        style={{
          backgroundImage: 'url("/images/campus-bg.jpg")',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
        }}
      />

      {/* Foreground Content */}
      <div className="relative z-10">
        {/* <-- HERE is your single nav --> */}
        <nav className="relative w-full z-50 transition-colors duration-300 shadow-md bg-transparent">
          
          {/* Logo on the left */}
          <div className="absolute left-10 top-2 flex items-center h-16">
            <Link href="/" className="flex items-center">
              <Image 
                src="/images/logo.png"
                alt="EventConnect Logo"
                width={150}
                height={40}
              />
            </Link>
          </div>

          {/* “Contact Us” button on the right */}
          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-end items-center h-16">
              <Link href="/contact">
                <button
                  className="
                    inline-flex 
                    items-center 
                    mt-2 
                    px-4 
                    py-2 
                    text-base 
                    font-medium 
                    rounded-md 
                    text-white 
                    hover:text-gray-300 
                    focus:outline-none 
                    transition-colors 
                    duration-150
                  "
                >
                  Contact Us
                </button>
              </Link>
            </div>
          </div>
        </nav>

        <main>{children}</main>
      </div>
    </div>
  );
}
