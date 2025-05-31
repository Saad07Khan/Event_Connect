import { useRouter } from 'next/router';
import Layout from '../../components/Layout';

export default function ErrorPage() {
  const router = useRouter();
  const { error } = router.query;

  return (
    <Layout>
      <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center">
        <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow-lg">
          <div>
            <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
              Authentication Error
            </h2>
            <p className="mt-2 text-center text-sm text-red-600">
              {error === 'AccessDenied' 
                ? 'Please use your college email address to sign in.'
                : 'An error occurred during authentication. Please try again.'}
            </p>
          </div>
          <div className="mt-8 space-y-6">
            <button
              onClick={() => router.push('/auth/signin')}
              className="w-full flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Back to Sign In
            </button>
          </div>
        </div>
      </div>
    </Layout>
  );
} 