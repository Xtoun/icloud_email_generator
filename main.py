import asyncio
import datetime
import os
from typing import Union, List, Optional
import re
import time

from rich.text import Text
from rich.prompt import IntPrompt
from rich.console import Console
from rich.table import Table

from icloud import HideMyEmail


MAX_CONCURRENT_TASKS = 10


class RichHideMyEmail(HideMyEmail):
    _cookie_file = "cookie.txt"

    def __init__(self):
        super().__init__()
        self.console = Console()
        self.table = Table()

        if os.path.exists(self._cookie_file):
            # load in a cookie string from file
            with open(self._cookie_file, "r") as f:
                self.cookies = [line for line in f if not line.startswith("//")][0]
        else:
            self.console.log(
                '[bold yellow][WARN][/] No "cookie.txt" file found! Generation might not work due to unauthorized access.'
            )

    async def _generate_one(self) -> Union[str, None]:
        # First, generate an email
        gen_res = await self.generate_email()

        if not gen_res:
            return
        elif "success" not in gen_res or not gen_res["success"]:
            error = gen_res["error"] if "error" in gen_res else {}
            err_msg = "Unknown"
            if type(error) == int and "reason" in gen_res:
                err_msg = gen_res["reason"]
            elif type(error) == dict and "errorMessage" in error:
                err_msg = error["errorMessage"]
            self.console.log(
                f"[bold red][ERR][/] - Failed to generate email. Reason: {err_msg}"
            )
            return

        email = gen_res["result"]["hme"]
        self.console.log(f'[50%] "{email}" - Successfully generated')

        # Then, reserve it
        reserve_res = await self.reserve_email(email)

        if not reserve_res:
            return
        elif "success" not in reserve_res or not reserve_res["success"]:
            error = reserve_res["error"] if "error" in reserve_res else {}
            err_msg = "Unknown"
            if type(error) == int and "reason" in reserve_res:
                err_msg = reserve_res["reason"]
            elif type(error) == dict and "errorMessage" in error:
                err_msg = error["errorMessage"]
            self.console.log(
                f'[bold red][ERR][/] "{email}" - Failed to reserve email. Reason: {err_msg}'
            )
            return

        self.console.log(f'[100%] "{email}" - Successfully reserved')
        return email

    async def _generate(self, num: int):
        emails = []
        for i in range(num):
            email = await self._generate_one()
            if email:
                emails.append(email)
            
            # Добавляем задержку 5 секунд между генерацией почт (кроме последней)
            if i < num - 1:
                self.console.log("[yellow]Waiting 5 seconds before next email generation...[/]")
                await asyncio.sleep(5)
        
        return emails

    async def generate(self, count: Optional[int]) -> List[str]:
        try:
            emails = []
            self.console.rule()
            if count is None:
                s = IntPrompt.ask(
                    Text.assemble(("How many iCloud emails you want to generate?")),
                    console=self.console,
                )

                count = int(s)
            self.console.log(f"Generating {count} email(s)...")
            self.console.rule()

            with self.console.status(f"[bold green]Generating iCloud email(s)..."):
                # Генерируем все почты последовательно с задержками
                batch = await self._generate(count)
                emails += batch

            if len(emails) > 0:
                with open("emails.txt", "a+") as f:
                    f.write(os.linesep.join(emails) + os.linesep)

                self.console.rule()
                self.console.log(
                    f':star: Emails have been saved into the "emails.txt" file'
                )

                self.console.log(
                    f"[bold green]All done![/] Successfully generated [bold green]{len(emails)}[/] email(s)"
                )

            return emails
        except KeyboardInterrupt:
            return []

    async def list(self, active: bool, search: str) -> None:
        gen_res = await self.list_email()
        if not gen_res:
            return

        if "success" not in gen_res or not gen_res["success"]:
            error = gen_res["error"] if "error" in gen_res else {}
            err_msg = "Unknown"
            if type(error) == int and "reason" in gen_res:
                err_msg = gen_res["reason"]
            elif type(error) == dict and "errorMessage" in error:
                err_msg = error["errorMessage"]
            self.console.log(
                f"[bold red][ERR][/] - Failed to generate email. Reason: {err_msg}"
            )
            return

        self.table.add_column("Label")
        self.table.add_column("Hide my email")
        self.table.add_column("Created Date Time")
        self.table.add_column("IsActive")

        for row in gen_res["result"]["hmeEmails"]:
            if row["isActive"] == active:
                if search is not None and re.search(search, row["label"]):
                    self.table.add_row(
                        row["label"],
                        row["hme"],
                        str(
                            datetime.datetime.fromtimestamp(
                                row["createTimestamp"] / 1000
                            )
                        ),
                        str(row["isActive"]),
                    )
                else:
                    self.table.add_row(
                        row["label"],
                        row["hme"],
                        str(
                            datetime.datetime.fromtimestamp(
                                row["createTimestamp"] / 1000
                            )
                        ),
                        str(row["isActive"]),
                    )

        self.console.print(self.table)

    async def auto_generate_scheduler(self, max_emails: int = 750):
        """Автоматическая генерация 5 почт каждый час до достижения лимита"""
        self.console.log("[bold blue]Starting automatic email generation scheduler...[/]")
        self.console.log(f"[blue]Will generate 5 emails every hour with 5-second delays between each[/]")
        self.console.log(f"[blue]Maximum emails to generate: {max_emails}[/]")
        
        total_generated = 0
        
        while total_generated < max_emails:
            try:
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                remaining = max_emails - total_generated
                emails_to_generate = min(5, remaining)
                
                self.console.log(f"[green]Starting scheduled generation at {current_time}[/]")
                self.console.log(f"[blue]Emails generated so far: {total_generated}/{max_emails}[/]")
                self.console.log(f"[blue]Generating {emails_to_generate} emails in this cycle[/]")
                
                # Генерируем почты
                emails = await self.generate(emails_to_generate)
                
                if emails:
                    total_generated += len(emails)
                    self.console.log(f"[green]Successfully generated {len(emails)} emails in this cycle[/]")
                    self.console.log(f"[green]Total generated: {total_generated}/{max_emails}[/]")
                else:
                    self.console.log("[yellow]No emails were generated in this cycle[/]")
                
                # Проверяем, достигли ли лимита
                if total_generated >= max_emails:
                    self.console.log(f"[bold green]🎉 Target reached! Generated {total_generated} emails total.[/]")
                    break
                
                # Ждем 1 час (3600 секунд) до следующей генерации
                self.console.log("[blue]Waiting 1 hour until next generation cycle...[/]")
                await asyncio.sleep(3600)
                
            except KeyboardInterrupt:
                self.console.log(f"[yellow]Auto-generation stopped by user. Generated {total_generated} emails total.[/]")
                break
            except Exception as e:
                self.console.log(f"[red]Error in auto-generation: {e}[/]")
                self.console.log("[blue]Retrying in 5 minutes...[/]")
                await asyncio.sleep(300)  # Ждем 5 минут при ошибке


async def generate(count: Optional[int]) -> None:
    async with RichHideMyEmail() as hme:
        await hme.generate(count)


async def list(active: bool, search: str) -> None:
    async with RichHideMyEmail() as hme:
        await hme.list(active, search)


async def auto_generate(max_emails: int = 750) -> None:
    """Запуск автоматической генерации 5 почт каждый час до достижения лимита"""
    async with RichHideMyEmail() as hme:
        await hme.auto_generate_scheduler(max_emails)


async def interactive_main():
    """Интерактивное меню для выбора типа генерации"""
    console = Console()
    
    console.print("\n[bold blue]🍎 iCloud Hide My Email Generator[/]")
    console.print("[blue]Choose generation mode:[/]\n")
    
    console.print("1. [yellow]Automatic generation[/] - Generate 5 emails every hour (up to 750 total)")
    console.print("2. [cyan]List existing emails[/] - View your current emails")
    console.print("3. [red]Exit[/] - Quit the program\n")
    
    while True:
        try:
            choice = IntPrompt.ask(
                Text.assemble("Select option (1-3)"),
                console=console,
                default=1
            )
            
            if choice == 1:
                # Автоматическая генерация
                max_emails = IntPrompt.ask(
                    Text.assemble("Maximum emails to generate (default: 750)"),
                    console=console,
                    default=750
                )
                if max_emails > 750:
                    console.print("[red]Maximum 750 emails allowed![/]")
                    max_emails = 750
                await auto_generate(max_emails)
                break
                
            elif choice == 2:
                # Просмотр списка
                await list(True, None)
                console.print("\n[blue]Press Enter to continue...[/]")
                input()
                continue
                
            elif choice == 3:
                # Выход
                console.print("[green]Goodbye![/]")
                break
                
            else:
                console.print("[red]Invalid choice! Please select 1-3.[/]")
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Operation cancelled by user.[/]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/]")
            break


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(interactive_main())
    except KeyboardInterrupt:
        pass
