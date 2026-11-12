export const navigation=[['overview','归并总览'],['datasets','曲线样本'],['policies','对齐口径'],['studies','归并任务'],['results','矩阵与合并树'],['reviews','人工命名复核']] as const;
export type Page=typeof navigation[number][0];
