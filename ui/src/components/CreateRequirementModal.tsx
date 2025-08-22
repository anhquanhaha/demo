"use client";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter, DialogTrigger } from "@/components/ui/dialog";
import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "./ui/form";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const formSchema = z.object({
  title: z.string().min(1, { message: "Tiêu đề là bắt buộc" }),
  pbi_requirement: z.string().min(1, { message: "Yêu cầu PBI là bắt buộc" }),
  file_attachment: z.any().optional(),
});

export default function CreateRequirementModal() {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      title: "",
      pbi_requirement: "",
      file_attachment: undefined,
    },
  });

  function onSubmit(values: z.infer<typeof formSchema>) {
    console.log(values);
  }

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button size={"sm"}>Thêm yêu cầu mới</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Thêm yêu cầu mới</DialogTitle>
        </DialogHeader>
        <DialogDescription>
          Thêm yêu cầu Test Case mới.
        </DialogDescription>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
            <FormField
              control={form.control}
              name="title"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Tên</FormLabel>
                  <FormControl>
                    <Input placeholder="Nhập tên yêu cầu" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="pbi_requirement"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Yêu cầu PBI</FormLabel>
                  <FormControl>
                    <Textarea placeholder="Nhập mô tả yêu cầu" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="file_attachment"
              render={({ field: { onChange, value, ...field } }) => (
                <FormItem>
                  <FormLabel>File đính kèm (Ảnh UI,...)</FormLabel>
                  <FormControl>
                    <Input 
                      type="file" 
                      accept="image/*,.pdf,.doc,.docx"
                      {...field}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                        const file = e.target.files?.[0];
                        onChange(file);
                      }}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <Button size={"sm"} variant={"outline"}>Thêm yêu cầu</Button>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}