// types.ts
export interface CategoryItem {
  id: number;
  name: string;
}

// 场景类型接口
export interface Category {
  id: string;
  name: string;
  items: CategoryItem[];
}


// 任务类型接口
export interface Task  {
  id: number;
  sceneId: number;
  sceneName: string;
  taskStatus: number;
  createdTime: string;
  updateTime: string;
}