from sqlalchemy.orm import Mapped, mapped_column, registry

table_registry = registry()


@table_registry.mapped_as_dataclass
class Client:
    __tablename__ = 'clients'
    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str]
    cpf: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
