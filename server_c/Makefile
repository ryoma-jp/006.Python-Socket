TARGET   = server
CC       = gcc
CFLAGS   = -MMD -MP
SRCS     = server.c
OBJS     = $(SRCS:%.c=%.o)
DEPS     = $(SRCS:%.c=%.d)
LIBS     = -lopencv_core -lopencv_highgui
RM       = rm

all : $(TARGET)

-include $(DEPS)

$(TARGET) : $(OBJS)
	$(CC) -o $@ $(OBJS)

.c.o :
	$(CC) -c $(CFLAGS) $<

clean :
	$(RM) -f $(TARGET) $(OBJS) $(DEPS)
