import { Button } from "@/components/ui/button";
import CreateRequirementModal from "@/components/CreateRequirementModal";
import Image from "next/image";

export default function Home() {
  return (
    <div className="flex flex-col gap-y-4">
      <div className="flex justify-between items-center">
        <h1>Danh sách yêu cầu đã tạo</h1>
        <CreateRequirementModal />
      </div>
    </div>
  );
}
