import React, { useState, useEffect, useRef } from 'react';
import { UploadCloud, FileText, CheckCircle, AlertCircle, Loader2, Search, BookOpen, File as FileIcon, Trash2 } from 'lucide-react';

// Interfaces for our API responses
interface DocumentInfo {
  id: string;
  filename: string;
  document_type: string;
  upload_date: string;
  status: string;
  chunks: number;
}

interface RagSource {
  document_id: string;
  page?: string;
  type?: string;
  authority?: string;
}

interface RagResponse {
  status: string;
  answer: string;
  sources: RagSource[];
  confidence: number;
}

export const KnowledgeBase: React.FC = () => {
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [loadingDocs, setLoadingDocs] = useState<boolean>(true);
  
  // Upload State
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<boolean>(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Query State
  const [query, setQuery] = useState('');
  const [querying, setQuerying] = useState<boolean>(false);
  const [queryResult, setQueryResult] = useState<RagResponse | null>(null);
  const [queryError, setQueryError] = useState<string | null>(null);

  const API_BASE_URL = 'http://127.0.0.1:8000';

  const fetchDocuments = async () => {
    try {
      setLoadingDocs(true);
      const res = await fetch(`${API_BASE_URL}/knowledge/documents`);
      if (!res.ok) throw new Error('Failed to fetch documents');
      const data = await res.json();
      setDocuments(data.documents || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingDocs(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFile(e.target.files[0]);
      setUploadError(null);
      setUploadSuccess(false);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      // Validate it's a supported file based on our loader
      const file = e.dataTransfer.files[0];
      const name = file.name.toLowerCase();
      if (name.endsWith('.md') || name.endsWith('.txt') || name.endsWith('.pdf') || name.endsWith('.doc') || name.endsWith('.docx')) {
        setSelectedFile(file);
        setUploadError(null);
        setUploadSuccess(false);
      } else {
        setUploadError("Only .md, .txt, .pdf, .doc, and .docx files are supported.");
      }
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setUploadError(null);
    setUploadSuccess(false);

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('document_type', 'SOP'); // Default type for now

    try {
      const res = await fetch(`${API_BASE_URL}/knowledge/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || 'Upload failed');
      }

      setUploadSuccess(true);
      setSelectedFile(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
      fetchDocuments();
    } catch (err: any) {
      setUploadError(err.message || 'An error occurred during upload');
    } finally {
      setUploading(false);
    }
  };

  const [deletingId, setDeletingId] = useState<string | null>(null);

  const handleDelete = async (docId: string) => {
    if (!window.confirm("Are you sure you want to delete this document?")) return;
    
    setDeletingId(docId);
    try {
      const res = await fetch(`${API_BASE_URL}/knowledge/documents/${docId}`, {
        method: 'DELETE'
      });
      if (!res.ok) throw new Error('Failed to delete document');
      await fetchDocuments(); // Refresh list
    } catch (err: any) {
      alert(err.message || 'Error deleting document');
    } finally {
      setDeletingId(null);
    }
  };

  const handleQuery = async () => {
    if (!query.trim()) return;

    setQuerying(true);
    setQueryError(null);
    setQueryResult(null);

    try {
      const res = await fetch(`${API_BASE_URL}/knowledge/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });

      if (!res.ok) {
        throw new Error('Query failed');
      }

      const data = await res.json();
      setQueryResult(data);
    } catch (err: any) {
      setQueryError(err.message || 'An error occurred while querying the knowledge base');
    } finally {
      setQuerying(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* HEADER SECTION */}
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">Knowledge Base</h1>
        <p className="text-sm text-slate-500 mt-1">
          Upload documents to build and manage your knowledge base.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        <div className="lg:col-span-2 space-y-6">
          {/* UPLOAD SECTION */}
          <div className="bg-white p-6 rounded-xl border border-[#E2E8F0] shadow-sm">
            <h2 className="text-lg font-medium text-slate-900 mb-4 flex items-center">
              <UploadCloud className="w-5 h-5 mr-2 text-primary" /> Upload Document
            </h2>
            
            <div 
              className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors ${
                selectedFile ? 'border-primary bg-blue-50/30' : 'border-slate-300 hover:border-slate-400'
              }`}
              onDragOver={handleDragOver}
              onDrop={handleDrop}
            >
              {!selectedFile ? (
                <div className="flex flex-col items-center">
                  <div className="w-12 h-12 bg-blue-50 text-blue-500 rounded-full flex items-center justify-center mb-3">
                    <UploadCloud size={24} />
                  </div>
                  <p className="text-sm font-medium text-slate-700 mb-1">Drag and drop your file here</p>
                  <p className="text-xs text-slate-500 mb-4">Supported formats: .md, .txt, .pdf, .doc, .docx</p>
                  <button 
                    onClick={() => fileInputRef.current?.click()}
                    className="px-4 py-2 bg-white border border-slate-300 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors"
                  >
                    Browse Files
                  </button>
                  <input 
                    type="file" 
                    ref={fileInputRef} 
                    onChange={handleFileChange} 
                    className="hidden" 
                    accept=".md,.txt,.pdf,.doc,.docx"
                  />
                </div>
              ) : (
                <div className="flex flex-col items-center">
                  <div className="w-12 h-12 bg-green-50 text-green-500 rounded-full flex items-center justify-center mb-3">
                    <FileText size={24} />
                  </div>
                  <p className="text-sm font-medium text-slate-900">{selectedFile.name}</p>
                  <p className="text-xs text-slate-500 mb-4">{formatFileSize(selectedFile.size)}</p>
                  
                  <div className="flex space-x-3">
                    <button 
                      onClick={() => {
                        setSelectedFile(null);
                        setUploadError(null);
                        setUploadSuccess(false);
                      }}
                      disabled={uploading}
                      className="px-4 py-2 bg-white border border-slate-300 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors disabled:opacity-50"
                    >
                      Cancel
                    </button>
                    <button 
                      onClick={handleUpload}
                      disabled={uploading}
                      className="px-4 py-2 bg-primary text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors flex items-center disabled:opacity-70"
                    >
                      {uploading ? <><Loader2 size={16} className="animate-spin mr-2" /> Uploading...</> : 'Upload & Process'}
                    </button>
                  </div>
                </div>
              )}
            </div>

            {uploadError && (
              <div className="mt-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm flex items-start border border-red-100">
                <AlertCircle size={16} className="mr-2 mt-0.5 flex-shrink-0" />
                <span>{uploadError}</span>
              </div>
            )}
            
            {uploadSuccess && (
              <div className="mt-4 p-3 bg-green-50 text-green-700 rounded-lg text-sm flex items-start border border-green-100">
                <CheckCircle size={16} className="mr-2 mt-0.5 flex-shrink-0" />
                <span>Document successfully processed and added to the Knowledge Base!</span>
              </div>
            )}
          </div>

          {/* UPLOADED DOCUMENTS SECTION */}
          <div className="bg-white p-6 rounded-xl border border-[#E2E8F0] shadow-sm">
            <h2 className="text-lg font-medium text-slate-900 mb-4 flex items-center justify-between">
              <div className="flex items-center">
                <BookOpen className="w-5 h-5 mr-2 text-slate-500" /> Uploaded Documents
              </div>
              <span className="text-xs font-medium bg-slate-100 text-slate-600 py-1 px-2 rounded-full">
                {documents.length} Docs
              </span>
            </h2>

            {loadingDocs ? (
              <div className="py-8 flex justify-center items-center text-slate-400">
                <Loader2 className="animate-spin w-6 h-6 mr-2" /> Loading documents...
              </div>
            ) : documents.length === 0 ? (
              <div className="py-10 text-center border border-dashed rounded-lg bg-slate-50">
                <FileIcon className="w-10 h-10 text-slate-300 mx-auto mb-2" />
                <p className="text-slate-500 text-sm">No documents in the knowledge base yet.</p>
              </div>
            ) : (
              <div className="overflow-hidden border rounded-lg">
                <table className="w-full text-left text-sm text-slate-600">
                  <thead className="bg-slate-50 border-b text-xs uppercase font-semibold text-slate-500">
                    <tr>
                      <th className="px-4 py-3">Document</th>
                      <th className="px-4 py-3">Type</th>
                      <th className="px-4 py-3">Date</th>
                      <th className="px-4 py-3">Status</th>
                      <th className="px-4 py-3 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {documents.map((doc, idx) => (
                      <tr key={idx} className="hover:bg-slate-50/50">
                        <td className="px-4 py-3 font-medium text-slate-900 flex items-center">
                          <FileText size={14} className="text-slate-400 mr-2" />
                          {doc.filename}
                        </td>
                        <td className="px-4 py-3">
                          <span className="px-2 py-1 bg-slate-100 rounded text-xs">{doc.document_type}</span>
                        </td>
                        <td className="px-4 py-3 text-slate-500">
                          {new Date(doc.upload_date).toLocaleDateString()}
                        </td>
                        <td className="px-4 py-3">
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-50 text-green-700 border border-green-200">
                            <span className="w-1.5 h-1.5 rounded-full bg-green-500 mr-1.5"></span>
                            {doc.status}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-right">
                          <button
                            onClick={() => handleDelete(doc.id)}
                            disabled={deletingId === doc.id}
                            className="text-slate-400 hover:text-red-600 transition-colors disabled:opacity-50"
                            title="Delete Document"
                          >
                            {deletingId === doc.id ? <Loader2 size={16} className="animate-spin" /> : <Trash2 size={16} />}
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

        {/* RAG QUERY TEST SECTION */}
        <div className="lg:col-span-1">
          <div className="bg-white p-6 rounded-xl border border-[#E2E8F0] shadow-sm sticky top-6">
            <h2 className="text-lg font-medium text-slate-900 mb-4 flex items-center">
              <Search className="w-5 h-5 mr-2 text-primary" /> Test Retrieval
            </h2>
            
            <div className="space-y-4">
              <div>
                <textarea
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Ask something about your uploaded documents..."
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary resize-none h-24"
                  disabled={querying}
                />
              </div>
              
              <button
                onClick={handleQuery}
                disabled={querying || !query.trim()}
                className="w-full px-4 py-2 bg-primary text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors flex justify-center items-center disabled:opacity-50"
              >
                {querying ? <><Loader2 size={16} className="animate-spin mr-2" /> Searching...</> : 'Ask Knowledge Base'}
              </button>
            </div>

            {queryError && (
              <div className="mt-4 p-3 bg-red-50 text-red-700 rounded-lg text-xs">
                {queryError}
              </div>
            )}

            {queryResult && (
              <div className="mt-6 border-t pt-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Answer</span>
                  {queryResult.confidence !== undefined && (
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                      queryResult.confidence >= 0.8 ? 'bg-green-100 text-green-800' : 'bg-amber-100 text-amber-800'
                    }`}>
                      Confidence: {(queryResult.confidence * 100).toFixed(0)}%
                    </span>
                  )}
                </div>
                
                <div className="bg-slate-50 p-3 rounded-lg text-sm text-slate-800 mb-4 border leading-relaxed">
                  {queryResult.answer}
                </div>

                {queryResult.sources && queryResult.sources.length > 0 && (
                  <div>
                    <span className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2 block">Sources</span>
                    <ul className="space-y-2">
                      {queryResult.sources.map((src, i) => (
                        <li key={i} className="text-xs bg-white border rounded p-2 text-slate-600 flex items-start">
                          <BookOpen size={12} className="mr-1.5 mt-0.5 text-slate-400 flex-shrink-0" />
                          <span>
                            <strong>{src.document_id}</strong>
                            {src.page && ` (Page ${src.page})`}
                            {src.type && ` • Type: ${src.type}`}
                            {src.authority && ` • Authority: ${src.authority}`}
                          </span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
};
