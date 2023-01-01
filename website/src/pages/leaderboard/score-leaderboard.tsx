import { HiBarsArrowDown } from "react-icons/hi2";
import RankItem from "src/components/RankItem";

const LeaderBoard = () => {
  const PlaceHolderProps = { username: "test_user", score: 10 };
  return (
    <div className="p-6 bg-slate-100 text-gray-800">
      <div className="flex flex-col">
        <div className="rounded-lg shadow-lg h-full block bg-white">
          <div className="p-8">
            <h5 className="text-2xl font-bold">LeaderBoard</h5>
          </div>
          <div className="flex flex-row justify-between px-6 py-3 font-semibold text-md">
            <div className="flex flex-row items-center justify-center space-x-2">
              <div>
                <p>Rank</p>
              </div>
              <div className="mt-2  text-slate-400 hover:text-sky-400 hover:cursor-pointer">
                <HiBarsArrowDown className="w-6 h-6 text-inherit"></HiBarsArrowDown>
              </div>
            </div>
            <div className="flex flex-row items-center justify-center space-x-2">
              <div>
                <p>User</p>
              </div>
              <div className="mt-2 text-slate-400 hover:text-sky-400 hover:cursor-pointer">
                <HiBarsArrowDown className="w-6 h-6 text-inherit"></HiBarsArrowDown>
              </div>
            </div>
            <div className="flex flex-row items-center justify-center space-x-2">
              <div>
                <p>Score</p>
              </div>
              <div className="mt-2  text-slate-400 hover:text-sky-400 hover:cursor-pointer">
                <HiBarsArrowDown className="w-6 h-6 text-inherit"></HiBarsArrowDown>
              </div>
            </div>
            <div className="flex flex-row items-center justify-center space-x-2">
              <div>
                <p>Medal</p>
              </div>
            </div>
          </div>
          {/* leaderboard items */}
          <RankItem {...PlaceHolderProps}></RankItem>
        </div>
      </div>
    </div>
  );
};

export default LeaderBoard;
