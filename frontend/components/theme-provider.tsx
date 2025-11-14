"use client";
import { ThemeProvider as NextThemesProvider } from "next-themes";
import Header from "./custom/Header";

export function ThemeProvider({
  children,
  ...props
}: React.ComponentProps<typeof NextThemesProvider>) {
  return (
    <NextThemesProvider {...props}>
      <Header></Header>
      {children}
    </NextThemesProvider>
  );
}
