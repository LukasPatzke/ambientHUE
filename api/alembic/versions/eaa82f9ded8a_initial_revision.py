"""initial revision

Revision ID: eaa82f9ded8a
Revises:
Create Date: 2020-11-06 15:30:25.194880

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eaa82f9ded8a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'bridge',
        sa.Column('id', sa.String(length=16), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('ipaddress', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'curve',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('kind', sa.String(length=50), nullable=False),
        sa.Column('default', sa.Boolean(), nullable=False),
        sa.Column('offset', sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'group',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('type', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('smart_off', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'status',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'webhook',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('on', sa.Boolean(), nullable=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('url', sa.String(), nullable=True),
        sa.Column('body', sa.String(), nullable=True),
        sa.Column('method', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'association_group_webhook',
        sa.Column('group_id', sa.Integer(), nullable=True),
        sa.Column('webhook_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['group_id'], ['group.id'], ),
        sa.ForeignKeyConstraint(['webhook_id'], ['webhook.id'], )
    )
    op.create_table(
        'header',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('value', sa.String(), nullable=True),
        sa.Column('webhook_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['webhook_id'], ['webhook.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'light',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('type', sa.String(), nullable=True),
        sa.Column('modelid', sa.String(), nullable=True),
        sa.Column('manufacturername', sa.String(), nullable=True),
        sa.Column('productname', sa.String(), nullable=True),
        sa.Column('on', sa.Boolean(), nullable=True),
        sa.Column('on_controlled', sa.Boolean(), nullable=True),
        sa.Column('on_threshold', sa.Float(), nullable=True),
        sa.Column('bri_controlled', sa.Boolean(), nullable=True),
        sa.Column('bri_max', sa.Float(), nullable=True),
        sa.Column('ct_controlled', sa.Boolean(), nullable=True),
        sa.Column('smart_off_on', sa.Boolean(), nullable=True),
        sa.Column('smart_off_bri', sa.Integer(), nullable=True),
        sa.Column('smart_off_ct', sa.Integer(), nullable=True),
        sa.Column('bri_curve_id', sa.Integer(), nullable=True),
        sa.Column('ct_curve_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['bri_curve_id'], ['curve.id'], ),
        sa.ForeignKeyConstraint(['ct_curve_id'], ['curve.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'point',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('x', sa.Integer(), nullable=False),
        sa.Column('y', sa.Integer(), nullable=False),
        sa.Column('first', sa.Boolean(), nullable=True),
        sa.Column('last', sa.Boolean(), nullable=True),
        sa.Column('curve_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['curve_id'], ['curve.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'association_group_light',
        sa.Column('light_id', sa.Integer(), nullable=True),
        sa.Column('group_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['group_id'], ['group.id'], ),
        sa.ForeignKeyConstraint(['light_id'], ['light.id'], )
    )
    op.create_table(
        'association_light_webhook',
        sa.Column('light_id', sa.Integer(), nullable=True),
        sa.Column('webhook_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['light_id'], ['light.id'], ),
        sa.ForeignKeyConstraint(['webhook_id'], ['webhook.id'], )
    )
    op.create_table(
        'position',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('visible', sa.Boolean(), nullable=True),
        sa.Column('light_id', sa.String(), nullable=True),
        sa.Column('group_id', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['group_id'], ['group.id'], ),
        sa.ForeignKeyConstraint(['light_id'], ['light.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('position')
    op.drop_table('association_light_webhook')
    op.drop_table('association_group_light')
    op.drop_table('point')
    op.drop_table('light')
    op.drop_table('header')
    op.drop_table('association_group_webhook')
    op.drop_table('webhook')
    op.drop_table('status')
    op.drop_table('settings')
    op.drop_table('group')
    op.drop_table('curve')
    op.drop_table('bridge')
    # ### end Alembic commands ###
