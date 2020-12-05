# Write your code here
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

Base = declarative_base()


class Table(Base):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True)
    task = Column(String, default='default_value')
    deadline = Column(Date, default=datetime.today())

    def __repr__(self):
        return self.task


engine = create_engine('sqlite:///todo.db?check_same_thread=False')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


def prepareList(rows, date=False):
    if len(rows) > 0:
        if date:
            return '\n'.join(list(map(
                            lambda x: f'{x[0] + 1}. {x[1].task}. {x[1].deadline.day} {x[1].deadline.strftime("%b")}',
                            enumerate(rows))
                        ))
        else:
            return '\n'.join(list(map(lambda x: f'{x[0] + 1}. {x[1].task}', enumerate(rows))))
    else:
        return "Nothing to do!"


def todayTasks():
    today = datetime.today()
    rows = session.query(Table).filter(Table.deadline == today.date()).order_by(Table.deadline).all()
    print(f"\nToday {today.day} {today.strftime('%b')}:\n" + prepareList(rows))


def weekTasks():
    today = datetime.today()
    rows = session.query(Table)\
        .filter(Table.deadline >= today.date())\
        .filter(Table.deadline <= (today + timedelta(days=7)).date())\
        .order_by(Table.deadline).all()
    s = []
    for i in range(7):
        d = today + timedelta(days=i)
        s.append(
            f"{d.strftime('%A')} {d.day} {d.strftime('%b')}:\n" +\
            prepareList([t for t in rows if t.deadline == d.date()])
        )
    print("\n\n".join(s))

def allTasks():
    print("All tasks:")
    rows = session.query(Table).order_by(Table.deadline).all()
    print(prepareList(rows, True))


def addTask():
    text = input("Enter task\n")
    try:
        dead = datetime.strptime(input("Enter deadline\n"), '%Y-%m-%d')
    except:
        session.add(Table(task=text))
    else:
        session.add(Table(task=text, deadline=dead))
    session.commit()
    print('The task has been added!\n')


def delTask():
    print("Choose the number of the task you want to delete:")
    rows = session.query(Table).order_by(Table.deadline).all()
    if len(rows) > 0:
        print(prepareList(rows, True))
        row = int(input())
        session.delete(rows[row-1])
        session.commit()
        print('The task has been deleted!')
    else:
        print("Nothing to delete")

def missedTasks():
    print("Missed tasks:")
    rows = session.query(Table).filter(Table.deadline < datetime.today().date()).order_by(Table.deadline).all()
    if len(rows) > 0:
        print(prepareList(rows, True))
    else:
        print("Nothing is missed!")


menu = [
    ["Today's tasks", todayTasks],
    ["Week's tasks", weekTasks],
    ["All tasks", allTasks],
    ["Missed tasks", missedTasks],
    ["Add task", addTask],
    ["Delete task", delTask]
]

menutext = "\n".join([f"{i + 1}) {t[0]}" for i, t in enumerate(menu)]) + "\n0) Exit\n"

while 1:
    a = input(menutext)
    print()
    m = menu[int(a)-1][1] if a.isnumeric() and int(a) in range(1, len(menu)+1) else None
    if m:
        m()
        print()
    else:
        print("Bye!")
        break
