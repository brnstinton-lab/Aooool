export interface DocSection {
  id: string;
  title: string;
  filename: string;
  content: string;
  icon: string;
}

export interface ProjectInfo {
  name: string;
  status: string;
  version: string;
  techStack: string[];
}
