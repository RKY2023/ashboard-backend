from django.core.management.base import BaseCommand
from expenses.models import Transaction, Expense
from expenses.services import ExpenseCategoryMapper


class Command(BaseCommand):
    help = 'Backfill expenses from existing transactions (debit only)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='Process transactions for specific user ID only',
        )

    def handle(self, *args, **options):
        """Create expense records for existing debit transactions"""

        # Get transactions with debit > 0 that don't have expenses yet
        transactions_query = Transaction.objects.filter(debit__gt=0)

        if options['user_id']:
            transactions_query = transactions_query.filter(user_id=options['user_id'])
            self.stdout.write(f'Processing transactions for user ID: {options["user_id"]}')

        # Exclude transactions that already have expenses
        transactions_query = transactions_query.filter(expense__isnull=True)

        total_transactions = transactions_query.count()
        self.stdout.write(f'Found {total_transactions} transactions to process')

        if total_transactions == 0:
            self.stdout.write(self.style.WARNING('No transactions to process'))
            return

        created_count = 0
        failed_count = 0
        user_mappers = {}  # Cache mappers per user

        for i, transaction in enumerate(transactions_query, 1):
            try:
                # Get or create mapper for this user
                if transaction.user_id not in user_mappers:
                    user_mappers[transaction.user_id] = ExpenseCategoryMapper(transaction.user)

                mapper = user_mappers[transaction.user_id]
                expense = mapper.create_expense_from_transaction(transaction)

                if expense:
                    created_count += 1
                    if created_count % 50 == 0:
                        self.stdout.write(f'Progress: {created_count}/{total_transactions}')
                else:
                    failed_count += 1

            except Exception as e:
                failed_count += 1
                self.stdout.write(
                    self.style.ERROR(f'Error processing transaction {transaction.id}: {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nDone! Created {created_count} expenses, {failed_count} failed.'
            )
        )
