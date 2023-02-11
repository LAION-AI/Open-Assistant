import React from "react";

import { Sortable } from "./Sortable";

// eslint-disable-next-line import/no-anonymous-default-export
export default {
  title: "Sortable/Sortable",
  component: Sortable,
};

const Template = ({ items, isEditable, isDisabled }) => {
  return <Sortable items={items} isEditable={isEditable} isDisabled={isDisabled} className="my-8" />;
};

const props = {
  items: [
    "Who were the 8 presidents before George Washington?",
    "euirdteunvglfe23908230892309832098 AAAAAAAA",
    "Sorry, my cat sat on my keyboard. Can you print a cat in ASCII art?",
    "This is a new line\nThis is a new line\nThis is a new line\nThis is a new line\nThis is a new line\nThis is a new line\nThis is a new line\nThis is a new line\nThis is a new line\nThis is a new line\n",
  ],
  isEditable: true,
  isDisabled: false,
};

export const Default = Template.bind({});
Default.args = props;

export const NotEditable = Template.bind({});
NotEditable.args = {
  ...props,
  isEditable: false,
};

export const LongText = Template.bind({});
LongText.args = {
  items: [
    "Okay, here\u2019s my answer.  The thing is, in a job interview you are applying to the position, right?  Which means that you need to try to make yourself sound as good a fit as possible.  So that means it\u2019s a mistake to wear something that people would think of as a silly or stupid outfit.  It\u2019s good to wear something in line with what people expect the job to require, and ideally you want to wear something that you can walk around comfortably in.  At the same time, if you wear something that looks kind of dorky, you might not stand out as much as someone who doesn\u2019t, because the other candidates probably all have something slightly weird or wacky about them too.  So, I\u2019d say, do you like your outfit?  Wear something that you\u2019re comfortable in, that you think you look good in, and is in line with what the job would require.  Also, for interview prep, I would focus on making yourself look as professional as possible, from your hair to your outfit.  What do you think of this?",
    "Assistant: Yes, I think they can be helpful when the child misbehaves, but they should be used with a little bit of compassion and understanding that it\u2019s not the natural state of things to have an adult yelling at them.  Time outs are also often used without letting the child know how they\u2019re getting out of the time out, which can make it feel arbitrary or like a punishment, rather than a consequence for something they did.  It\u2019s really easy for adults to do this kind of thing unconsciously.  It\u2019s easy to get caught up in the notion that \u201cThey\u2019re in time out, and that\u2019s the end of it!\u201d but kids can be pretty imaginative, and they can use their own creativity to make their way out of time outs.  A compassionate time out ends when the child shows a sign of understanding what they\u2019ve done wrong, and are ready to begin again.  That way the child knows they\u2019re learning, and that the parent is seeing them as an intelligent person, even if they sometimes mess up.  You can still use the other techniques you were using to be tough when necessary, but using a compassionate approach will let you use them without actually using them!",
    "Assistant: No.  The USA was founded by a Puritan group of Protestants, but it didn\u2019t adopt the religion of the Puritans until much later, and it was always a secular state.  The Puritans observed the Sabbath on Sunday, and the Puritans only had a small influence in the early history of the USA.  It\u2019s difficult to trace the origins of closing stores on Sunday, but one early and short-lived attempt at forcing the Sabbath on people in the 1800s was motivated by the Protestant ideal that people should spend Sunday focusing on spiritual activities.  By the mid-1800s, when the Sunday closing law was made, there was not a lot of pressure from that standpoint, but the church had begun to advocate for Sunday closing laws as a way of counteracting the negative effects of industrialization on the day of rest.  Even after that shift, closing stores on Sunday was not always possible, since the religious Sunday was not always chosen for observance.  And as industrialization accelerated and mechanization made it possible to operate stores on Sunday, the law was not enforced as much as people liked.  The day of rest was also being violated by stores that stayed open all day on Sunday, so closing stores on Sundays became an effort to protect the Sabbath for all citizens.",
    "This is a new line\nThis is a new line\nThis is a new line\nThis is a new line\nThis is a new line\nThis is a new line\nThis is a new line\nThis is a new line\nThis is a new line\nThis is a new line\nThis is a new line\nThis is a new line\nThis is a new line\nThis is a new line\n",
  ],
  isEditable: true,
  isDisabled: false,
};
