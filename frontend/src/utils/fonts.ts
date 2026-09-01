// 编辑器可选字体列表（自定义字体可选这里的选项；也可通过扩展入口接入 Google Fonts / 上传字体）
export interface FontOption {
  label: string
  value: string
}

export const FONT_OPTIONS: FontOption[] = [
  { label: '默认', value: '' },
  { label: '宋体', value: 'SimSun' },
  { label: '黑体', value: 'SimHei' },
  { label: '微软雅黑', value: 'Microsoft YaHei' },
  { label: '楷体', value: 'KaiTi' },
  { label: '仿宋', value: 'FangSong' },
  { label: '思源黑体', value: 'Noto Sans SC' },
  { label: '思源宋体', value: 'Noto Serif SC' },
  { label: 'Georgia', value: 'Georgia' },
  { label: 'Times New Roman', value: 'Times New Roman' },
  { label: 'Arial', value: 'Arial' },
  { label: 'Comic Sans MS', value: 'Comic Sans MS' },
]

export const FONT_SIZE_OPTIONS = [
  { label: '小', value: '12px' },
  { label: '正常', value: '16px' },
  { label: '中', value: '20px' },
  { label: '大', value: '24px' },
  { label: '特大', value: '32px' },
]