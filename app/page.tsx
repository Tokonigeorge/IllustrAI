'use client';

import { useState } from 'react';
import axios from 'axios';

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [promptText, setPromptText] = useState('');
  const [pdfFile, setPdfFile] = useState<File | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    setPdfFile(selectedFile || null);
  };

  const handleSubmit = async (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    if (!pdfFile || !promptText) {
      alert('Please select a PDF file and enter a prompt.');
      return;
    }
    setLoading(true);

    try {
      await axios
        .post('/api/py/process', {
          pdfFilename: pdfFile.name,
          prompt: promptText,
        })
        .then((response: any) => {
          if (response.data.success) {
            console.log('Success:', response.data.message);
          }
        })
        .catch((error: Error) => console.error(error));

      setLoading(false);
    } catch (error) {
      console.error('Error:', error);
      setLoading(false);
    }
  };

  return (
    <main className='flex min-h-screen flex-col items-center justify-between p-24'>
      <div className='z-10 w-full max-w-5xl items-center justify-between font-mono text-sm lg:flex'>
        <input type='file' accept='.pdf' onChange={handleFileChange} />
        <input
          type='text'
          value={promptText}
          onChange={(e) => setPromptText(e.target.value)}
          placeholder='Enter your prompt...'
        />
        <button
          onClick={(e) =>
            handleSubmit(e as React.MouseEvent<HTMLButtonElement>)
          }
        >
          {loading ? 'Processing...' : 'Send'}
        </button>
        {/* <p className='fixed left-0 top-0 flex w-full justify-center border-b border-gray-300 bg-gradient-to-b from-zinc-200 pb-6 pt-8 backdrop-blur-2xl dark:border-neutral-800 dark:bg-zinc-800/30 dark:from-inherit lg:static lg:w-auto  lg:rounded-xl lg:border lg:bg-gray-200 lg:p-4 lg:dark:bg-zinc-800/30'>
          Get started by editing FastApi API&nbsp;
          <Link href='/api/py/helloFastApi'>
            <code className='font-mono font-bold'>api/index.py</code>
          </Link>
        </p> */}
      </div>
    </main>
  );
}
