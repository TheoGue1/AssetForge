import { cn } from "@/lib/utils";

export type GalleryImage = {
  src: string;
  alt: string;
};

export function ImageGallery({
  images,
  className,
}: {
  images: GalleryImage[];
  className?: string;
}) {
  return (
    <div
      className={cn(
        "grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3",
        className,
      )}
      data-testid="image-gallery"
    >
      {images.map((image) => (
        // eslint-disable-next-line @next/next/no-img-element -- vitest-friendly; could swap to next/image later
        <img
          key={`${image.src}-${image.alt}`}
          src={image.src}
          alt={image.alt}
          className="h-auto w-full rounded-lg border border-zinc-800 object-cover"
        />
      ))}
    </div>
  );
}
