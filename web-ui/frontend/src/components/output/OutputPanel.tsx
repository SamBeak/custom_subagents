"use client";

import { FolderOpen, FileText, Download, ExternalLink } from "lucide-react";

interface OutputPaths {
	directory: string;
	idea_report: string;
	business_model: string;
	pitch_materials: string;
	summary: string;
}

interface OutputPanelProps {
	outputPaths: OutputPaths | null;
	isVisible: boolean;
}

export default function OutputPanel({ outputPaths, isVisible }: OutputPanelProps) {
	if (!isVisible || !outputPaths) {
		return null;
	}

	const files = [
		{ name: "README.md", path: outputPaths.summary, label: "요약" },
		{ name: "idea-report.md", path: outputPaths.idea_report, label: "아이디어 보고서" },
		{ name: "business-model.md", path: outputPaths.business_model, label: "비즈니스 모델" },
		{ name: "pitch-materials.md", path: outputPaths.pitch_materials, label: "피치 자료" },
	];

	const getFileName = (path: string) => {
		return path.split(/[/\\]/).pop() || path;
	};

	const getDirName = (path: string) => {
		const parts = path.split(/[/\\]/);
		return parts[parts.length - 1] || path;
	};

	return (
		<div className="bg-green-50 border border-green-200 rounded-lg p-4 m-4">
			<div className="flex items-center gap-2 mb-3">
				<FolderOpen className="w-5 h-5 text-green-600" />
				<h3 className="font-semibold text-green-800">산출물 저장 완료</h3>
			</div>

			<div className="bg-white rounded-md p-3 mb-3">
				<p className="text-xs text-gray-500 mb-1">저장 위치</p>
				<code className="text-sm text-gray-700 break-all">
					{getDirName(outputPaths.directory)}
				</code>
			</div>

			<div className="space-y-2">
				<p className="text-xs text-gray-500">생성된 파일</p>
				{files.map((file) => (
					<div
						key={file.name}
						className="flex items-center justify-between bg-white rounded-md px-3 py-2"
					>
						<div className="flex items-center gap-2">
							<FileText className="w-4 h-4 text-gray-400" />
							<span className="text-sm">{file.label}</span>
							<span className="text-xs text-gray-400">({file.name})</span>
						</div>
					</div>
				))}
			</div>

			<div className="mt-4 pt-3 border-t border-green-200">
				<p className="text-xs text-gray-500">
					📁 파일 탐색기에서 <code className="bg-gray-100 px-1 rounded">outputs</code> 폴더를 확인하세요
				</p>
			</div>
		</div>
	);
}
