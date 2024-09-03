from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'e031f2b4b53f'
down_revision = '63f1c50bc8e3'
branch_labels = None
depends_on = None

def upgrade():
    # rankカラムが存在しない場合のみ追加
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [column['name'] for column in inspector.get_columns('employees')]
    
    if 'rank' not in columns:
        op.add_column('employees', sa.Column('rank', sa.String(), nullable=True))
    
    # start_dateカラムのNOT NULL制約を変更するための手順
    shift_periods_columns = [column['name'] for column in inspector.get_columns('shift_periods')]
    
    if 'new_start_date' not in shift_periods_columns:
        op.add_column('shift_periods', sa.Column('new_start_date', sa.Date(), nullable=True))  # NULLを許可
        op.execute('UPDATE shift_periods SET new_start_date = start_date')
        op.drop_column('shift_periods', 'start_date')
        op.add_column('shift_periods', sa.Column('start_date', sa.Date(), nullable=True))  # NULLを許可
        op.execute('UPDATE shift_periods SET start_date = new_start_date')
        op.alter_column('shift_periods', 'start_date', nullable=False)  # NOT NULLに変更
        op.drop_column('shift_periods', 'new_start_date')

    if 'new_end_date' not in shift_periods_columns:
        op.add_column('shift_periods', sa.Column('new_end_date', sa.Date(), nullable=True))  # NULLを許可
        op.execute('UPDATE shift_periods SET new_end_date = end_date')
        op.drop_column('shift_periods', 'end_date')
        op.add_column('shift_periods', sa.Column('end_date', sa.Date(), nullable=True))  # NULLを許可
        op.execute('UPDATE shift_periods SET end_date = new_end_date')
        op.alter_column('shift_periods', 'end_date', nullable=False)  # NOT NULLに変更
        op.drop_column('shift_periods', 'new_end_date')

def downgrade():
    op.drop_column('employees', 'rank')
    # 逆の操作を行う場合は、元のカラムを再作成する必要があります