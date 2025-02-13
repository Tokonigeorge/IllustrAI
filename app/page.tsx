'use client';

import { useState } from 'react';
import axios from 'axios';
import Image from 'next/image';

export default function Home() {
  const [imageUrl, setImageUrl] = useState<string | null>(null);
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

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 300000000);

    try {
      const formData = new FormData();
      formData.append('file', pdfFile);

      //upload pdf to mongodb
      const uploadResponse = await axios.post(
        'http://127.0.0.1:8000/api/py/upload',
        formData
      );

      const fileId = uploadResponse.data.file_id;

      if (!fileId) throw new Error('Failed to upload PDF');
      await axios
        .post(
          'http://127.0.0.1:8000/api/py/process',
          {
            file_id: fileId,
            prompt: promptText,
          },
          {
            signal: controller.signal,
          }
        )
        .then((response: any) => {
          if (response.data.success) {
            console.log(
              'Success now:',
              response.data.results?.generated_image_url
            );
            setImageUrl(response.data.results?.generated_image_url);
            // setResults(
            //   Object.entries(response.data.results).map(([page, text]) =>
            //     (text as string).split('\n').join('\n')
            //   )
            // );
          }
        })
        .catch((error: Error) => console.error(error));

      setLoading(false);
    } catch (error) {
      clearTimeout(timeoutId); // Clean up timeout
      controller.abort();
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
      <div className='mt-4'>
        {imageUrl && (
          <Image
            src={imageUrl}
            alt='Generated image'
            width={500}
            height={500}
          />
        )}
      </div>
    </main>
  );
}
