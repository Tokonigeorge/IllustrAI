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
      const formData = new FormData();
      formData.append('file', pdfFile);

      //upload pdf to mongodb
      const uploadResponse = await axios.post('/api/py/upload', formData);

      const fileId = uploadResponse.data.file_id;

      if (!fileId) throw new Error('Failed to upload PDF');
      await axios
        .post('/api/py/process', {
          file_id: fileId,
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
      </div>
    </main>
  );
}
