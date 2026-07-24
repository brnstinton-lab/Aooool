import { useState } from 'react';
import { initialDocs } from './data/initialDocs';
import { DocSection } from './types';
import { 
  BookOpen, 
  FileText, 
  Layers, 
  Database, 
  Code2, 
  Compass,
  Search,
  Package,
  Palette,
  ShieldCheck,
  ListChecks,
  BookMarked,
  FolderTree, 
  Plus, 
  CheckCircle2, 
  Terminal,
  Copy,
  Check
} from 'lucide-react';

export default function App() {
  const [activeDocId, setActiveDocId] = useState<string>('foundation');
  const [docs] = useState<DocSection[]>(initialDocs);
  const [copied, setCopied] = useState<boolean>(false);

  const activeDoc = docs.find((doc) => doc.id === activeDocId) || docs[0];

  const renderIcon = (iconName: string) => {
    switch (iconName) {
      case 'Compass': return <Compass className="w-4 h-4" />;
      case 'Search': return <Search className="w-4 h-4" />;
      case 'Package': return <Package className="w-4 h-4" />;
      case 'Palette': return <Palette className="w-4 h-4" />;
      case 'ShieldCheck': return <ShieldCheck className="w-4 h-4" />;
      case 'ListChecks': return <ListChecks className="w-4 h-4" />;
      case 'BookMarked': return <BookMarked className="w-4 h-4" />;
      case 'BookOpen': return <BookOpen className="w-4 h-4" />;
      case 'FileText': return <FileText className="w-4 h-4" />;
      case 'Layers': return <Layers className="w-4 h-4" />;
      case 'Database': return <Database className="w-4 h-4" />;
      case 'Code2': return <Code2 className="w-4 h-4" />;
      default: return <FileText className="w-4 h-4" />;
    }
  };

  const handleCopyPath = (path: string) => {
    navigator.clipboard.writeText(path);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans">
      {/* Top Navbar */}
      <header className="bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between shadow-xs">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-emerald-600 text-white flex items-center justify-center font-black text-lg shadow-sm">
            AUL
          </div>
          <div>
            <h1 className="text-lg font-bold text-slate-900 leading-tight">AUL — Свой посёлок. Свои люди.</h1>
            <p className="text-xs text-slate-500">Документация & Архитектура приложения</p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> Material Design 3
          </span>
        </div>
      </header>

      {/* Main Container */}
      <div className="flex-1 flex flex-col md:flex-row max-w-7xl w-full mx-auto p-4 md:p-6 gap-6">
        {/* Sidebar */}
        <aside className="w-full md:w-64 bg-white rounded-xl border border-slate-200 p-4 shrink-0 shadow-xs flex flex-col">
          <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-100">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <FolderTree className="w-3.5 h-3.5" /> Файлы / docs
            </span>
          </div>

          <nav className="space-y-1">
            {docs.map((doc) => {
              const isActive = doc.id === activeDocId;
              return (
                <button
                  key={doc.id}
                  onClick={() => setActiveDocId(doc.id)}
                  className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-indigo-50 text-indigo-700 font-semibold'
                      : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                  }`}
                >
                  <span className={isActive ? 'text-indigo-600' : 'text-slate-400'}>
                    {renderIcon(doc.icon)}
                  </span>
                  <span className="truncate">{doc.title}</span>
                </button>
              );
            })}
          </nav>

          <div className="mt-8 pt-4 border-t border-slate-100">
            <div className="bg-slate-50 rounded-lg p-3 text-xs text-slate-600 space-y-2">
              <p className="font-medium text-slate-800 flex items-center gap-1">
                <Terminal className="w-3.5 h-3.5 text-indigo-600" /> Как передать документацию:
              </p>
              <p className="text-slate-500 leading-relaxed">
                Отправьте текст документации прямо в сообщения чата, и я распределю его по соответствующим файлам в каталоге <code className="bg-slate-200 px-1 py-0.5 rounded text-slate-800">docs/</code>.
              </p>
            </div>
          </div>
        </aside>

        {/* Content Viewer */}
        <main className="flex-1 bg-white rounded-xl border border-slate-200 p-6 shadow-xs flex flex-col">
          <div className="flex items-center justify-between border-b border-slate-100 pb-4 mb-6">
            <div>
              <div className="flex items-center gap-2 text-xs text-slate-400 mb-1">
                <span>/docs</span>
                <span>/</span>
                <span className="text-indigo-600 font-medium">{activeDoc.filename}</span>
              </div>
              <h2 className="text-xl font-bold text-slate-900">{activeDoc.title}</h2>
            </div>

            <button
              onClick={() => handleCopyPath(activeDoc.filename)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
              title="Скопировать путь к файлу"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Скопировано' : 'Путь к файлу'}</span>
            </button>
          </div>

          <div className="prose prose-slate max-w-none text-slate-700 whitespace-pre-line text-sm leading-relaxed bg-slate-50/50 p-6 rounded-lg border border-slate-100">
            {activeDoc.content}
          </div>

          {/* Quick Info Box */}
          <div className="mt-6 p-4 rounded-lg bg-indigo-50/60 border border-indigo-100 text-xs text-indigo-900 flex items-start gap-3">
            <Plus className="w-4 h-4 text-indigo-600 shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-indigo-950">Следующий шаг разработки</p>
              <p className="text-indigo-800/90 mt-0.5">
                Отправьте блок документации или опишите следующий шаг (например, структуру Django моделей, DRF API или пользовательский интерфейс).
              </p>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
